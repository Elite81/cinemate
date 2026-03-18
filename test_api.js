import http from 'k6/http';
import { check, group, sleep } from 'k6';

// 1. Performance Thresholds
export let options = {
    stages: [
        { duration: '30s', target: 20 }, // Ramp-up: 0 to 20 users
        { duration: '1m', target: 20 },  // Stay at 20 users (Load Test)
        { duration: '30s', target: 0 },  // Ramp-down to 0
    ],
    thresholds: {
        'http_req_duration': ['p(95)<2000'], // 95% of requests must be under 2s
        'http_req_failed': ['rate<0.01'],    // Error rate must be less than 1%
    },
};

const BASE_URL = 'http://127.0.0.1:8000';

export default function () {
    
    // Group 1: Landing Page (Testing Redis Cache Speed)
    group('Discovery Flow', function () {
        let homeRes = http.get(`${BASE_URL}/`);
        check(homeRes, {
            'homepage status is 200': (r) => r.status === 200,
            'homepage is fast (<500ms)': (r) => r.timings.duration < 500,
        });

        let genreRes = http.get(`${BASE_URL}/genre/Action`);
        check(genreRes, {
            'genre page status is 200': (r) => r.status === 200,
        });
        
        sleep(1);
    });

    // Group 2: Individual Movie Interaction
    group('Movie Detail Flow', function () {
        // Testing a specific movie ID (ensure this exists in your DB/TMDB)
        let movieRes = http.get(`${BASE_URL}/movie/550`); 
        check(movieRes, {
            'movie detail status is 200': (r) => r.status === 200,
            'contains movie info': (r) => r.body.includes('Overview') || r.body.includes('Release'),
        });

        sleep(2);
    });

    // Group 3: User Auth-Required Endpoints (Check for 302 Redirects if not logged in)
    group('Authenticated Features', function () {
        let favRes = http.get(`${BASE_URL}/favorites/`);
        check(favRes, {
            'favorites accessible or redirected': (r) => r.status === 200 || r.status === 302,
        });
    });

    // Simulate "Think Time" between 1 and 4 seconds
    sleep(Math.random() * 3 + 1);
}