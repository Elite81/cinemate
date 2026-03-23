import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 }, 
        { duration: '1m', target: 50 },  
        { duration: '30s', target: 0 },  
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], 
        http_req_failed: ['rate<0.01'], 
    },
};

const BASE_URL = 'http://127.0.0.1:8000';

// Optimized Login Function
function login(jar) {
    const LOGIN_URL = `${BASE_URL}/accounts/login/`;
    
    // 1. Initial GET to grab the CSRF cookie
    let res = http.get(LOGIN_URL, { jar: jar });

    // 2. Extract CSRF from the cookie jar
    let cookies = jar.cookiesForURL(BASE_URL);
    let csrftoken = (cookies.csrftoken && cookies.csrftoken.length > 0) ? cookies.csrftoken[0] : '';

    if (!csrftoken) {
        return null;
    }

    // 3. POST Credentials - One time only per VU
    let loginData = {
        username: 'Testuser', 
        password: 'Admin@Admin',
        csrfmiddlewaretoken: csrftoken,
    };

    return http.post(LOGIN_URL, loginData, {
        headers: { 
            'X-CSRFToken': csrftoken, 
            'Referer': LOGIN_URL,
        },
        jar: jar,
    });
}

export default function () {
    const jar = http.cookieJar();
    
    // --- AUTHENTICATION LAYER ---
    // __ITER === 0 means this only runs on the very first loop for each of the 50 VUs
    if (__ITER === 0) {
        login(jar);
    }

    let cookies = jar.cookiesForURL(BASE_URL);
    let csrftoken = (cookies.csrftoken && cookies.csrftoken.length > 0) ? cookies.csrftoken[0] : '';
    let movieId = Math.floor(Math.random() * 20) + 1;

    // --- TEST GROUPS ---
    group('01_Home_Page', function () {
        let res = http.get(`${BASE_URL}/`, { jar: jar });
        check(res, { 'status is 200': (r) => r.status === 200 });
    });

    group('02_Movie_Detail', function () {
        let res = http.get(`${BASE_URL}/movie/${movieId}/`, { jar: jar });
        check(res, { 'status is 200': (r) => r.status === 200 });
    });

    group('03_Social_Interactions', function () {
        // Only attempt if we have a valid session to avoid unnecessary 302/403s
        if (cookies.sessionid && csrftoken) {
            const params = {
                headers: { 'X-CSRFToken': csrftoken },
                jar: jar,
            };

            // Like Toggle
            let likeRes = http.post(`${BASE_URL}/liked/${movieId}/`, { csrfmiddlewaretoken: csrftoken }, params);
            check(likeRes, { 'Action Successful': (r) => r.status === 200 || r.status === 302 });

            // Comment Post
            let commentRes = http.post(`${BASE_URL}/comment/${movieId}/`, 
                { content: 'Performance Test', csrfmiddlewaretoken: csrftoken }, 
                params
            );
            check(commentRes, { 'Comment Successful': (r) => r.status === 200 || r.status === 302 });
        }
    });

    // Pacing: Wait 1 second before this VU starts the next loop
    sleep(1);
}


// export default function () {
//     const jar = http.cookieJar();
    
//     // 1. STAGGER: Spread users out so they don't hit the CPU all at once
//     sleep(Math.random() * 3); 

//     // 2. AUTH: Login once per VU session
//     let cookies = jar.cookiesForURL(BASE_URL);
//     if (!cookies.sessionid) {
//         login(jar);
//         cookies = jar.cookiesForURL(BASE_URL);
//     }

//     let csrftoken = cookies.csrftoken ? cookies.csrftoken[0] : '';
//     // Use IDs 1-20 (Make sure these are seeded in your DB!)
//     let movieId = Math.floor(Math.random() * 20) + 1;

//     // 3. THE TEST GROUPS
//     group('01_Home_Page_Cache', function () {
//         // Testing how fast Redis serves the movie list
//         let res = http.get(`${BASE_URL}/`, { jar: jar });
//         check(res, { 'Home Cache Hit': (r) => r.status === 200 });
//     });

//     group('02_Movie_Detail', function () {
//         let res = http.get(`${BASE_URL}/movie/${movieId}`, { jar: jar });
//         check(res, { 'Detail Loaded': (r) => r.status === 200 });
//     });

//     group('03_Post_Interactions', function () {
//         if (cookies.sessionid && csrftoken) {
//             // Test Like (Database Write)
//             let likeRes = http.post(`${BASE_URL}/liked/${movieId}`, 
//                 { csrfmiddlewaretoken: csrftoken },
//                 { headers: { 'X-CSRFToken': csrftoken }, jar: jar }
//             );
//             check(likeRes, { 'Like Registered': (r) => r.status === 200 || r.status === 302 });

//             // Test Comment (Database Write + Redis Invalidation if applicable)
//             let commentRes = http.post(`${BASE_URL}/comment/${movieId}`, 
//                 { content: 'k6 Performance Test Comment', csrfmiddlewaretoken: csrftoken },
//                 { headers: { 'X-CSRFToken': csrftoken }, jar: jar }
//             );
//             check(commentRes, { 'Comment Saved': (r) => r.status === 200 || r.status === 201 });
//         }
//     });

//     //Simulate "Think Time" before the next loop
//     sleep(1);
// }




// export default function () {
//     const jar = http.cookieJar();
    
//     sleep(Math.random() * 3); 

//     // AUTH: Login once
//     let cookies = jar.cookiesForURL(BASE_URL);
//     if (!cookies.sessionid) {
//         login(jar);
//         // Refresh local variable after the post
//         cookies = jar.cookiesForURL(BASE_URL);
//     }

//     group('01_Home_Page_Cache', function () {
//         let res = http.get(`${BASE_URL}/`, { jar: jar });
//         check(res, { 'Home Cache Hit': (r) => r.status === 200 });
//     });

//     group('03_Post_Interactions', function () {
//         // ALWAYS refresh here to get the LATEST state from the jar
//         let currentCookies = jar.cookiesForURL(BASE_URL);
//         let currentCsrf = (currentCookies.csrftoken && currentCookies.csrftoken.length > 0) 
//                           ? currentCookies.csrftoken[0] : '';

//         if (currentCookies.sessionid && currentCsrf) {
//             // SUCCESS: Execute your Like/Comment POSTs here
//             // console.log(`VU ${__VU} Authenticated!`);
//         } else {
//             console.error(`VU ${__VU} Auth Check - Session: ${!!currentCookies.sessionid}, CSRF: ${!!currentCsrf}`);
            
//             // If it still fails, let's see the cookies we DO have
//             // console.log(`Available cookies for VU ${__VU}: ${JSON.stringify(currentCookies)}`);
//         }
//     });

//     sleep(1);
// }