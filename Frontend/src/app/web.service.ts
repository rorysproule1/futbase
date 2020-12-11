import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()
export class WebService {

    private players_private_list;
    private playersSubject = new Subject();
    players_list = this.playersSubject.asObservable();

    private player_private_list;
    private playerSubject = new Subject();
    player_list = this.playerSubject.asObservable();

    private reviews_private_list;
    private reviewsSubject = new Subject();
    reviews_list = this.reviewsSubject.asObservable();

    private wishlist_private_list;
    private wishlistSubject = new Subject();
    wishlist_list = this.wishlistSubject.asObservable();

    playerID;

    constructor(private http: HttpClient) { }

    downvoteReview(review_id: string, sort: string) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.put(`http://localhost:5000/api/v1.0/reviews/${review_id}/downvote/${sessionStorage.user_id}`, {}, requestOptions).subscribe(response => {
            this.getReviews(this.playerID, sort)
        })

    }

    upvoteReview(review_id: string, sort: string) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.put(`http://localhost:5000/api/v1.0/reviews/${review_id}/upvote/${sessionStorage.user_id}`, {}, requestOptions).subscribe(response => {
            this.getReviews(this.playerID, sort)
        })

    }

    postToWishlist(base_id, player_id) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };

        let postData = new FormData();
        postData.append("base_id", base_id);
        postData.append("player_id", player_id);

        this.http.post(
            `http://localhost:5000/api/v1.0/users/${sessionStorage.user_id}/wishlist`,
            postData).subscribe(
                response => {
                    this.getWishlist();
                    console.log(response)
                });
    }

    attemptLogin(credentials) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/login?username=' + credentials.username + "&password=" + credentials.password
        ).subscribe(response => {
            var resp = JSON.stringify(response)
            let resJSON = JSON.parse(resp);

            // set session values for user
            sessionStorage.setItem("admin", resJSON["admin"])
            sessionStorage.setItem("email", resJSON["email"])
            sessionStorage.setItem("token", resJSON["token"])
            sessionStorage.setItem("user_id", resJSON["user_id"])

            window.location.href = "/"

        });
    }

    logOut() {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.get(
            'http://localhost:5000/api/v1.0/logout', requestOptions
        ).subscribe(response => {
            window.location.href = "/login"
            sessionStorage.clear()
        });
    }

    getPlayers(page: Number, filters) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };

        // get filter params for player search
        let query_params = "&"
        if (filters.name) {
            query_params += "name=" + filters.name + "&"
        }
        if (filters.overall) {
            query_params += "overall=" + filters.overall + "&"
        }
        if (filters.position) {
            query_params += "position=" + filters.position + "&"
        }
        if (filters.nationality) {
            query_params += "nationality=" + filters.nationality + "&"
        }
        if (filters.league) {
            query_params += "league=" + filters.league + "&"
        }
        if (filters.club) {
            query_params += "club=" + filters.club + "&"
        }
        if (filters.quality) {
            query_params += "quality=" + filters.quality + "&"
        }
        if (filters.revision) {
            query_params += "revision=" + filters.revision + "&"
        }
        return this.http.get(
            'http://localhost:5000/api/v1.0/players?pn=' + page + query_params, requestOptions
        ).subscribe(response => {
            this.players_private_list = response;
            this.playersSubject.next(
                this.players_private_list);
            console.log(response)
            sessionStorage.setItem("player_count", response[0]["player_count"])
        });
    }

    getPlayer(id: string) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.get(
            'http://localhost:5000/api/v1.0/players/' + id, requestOptions)
            .subscribe(response => {
                let player_array = [];
                player_array.push(response)
                this.player_private_list = player_array;
                this.playerSubject.next(
                    this.player_private_list);
                this.playerID = id;
                console.log(response)
            });
    }

    getWishlist() {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.get(
            `http://localhost:5000/api/v1.0/users/${sessionStorage.user_id}/wishlist`, requestOptions)
            .subscribe(
                response => {
                    this.wishlist_private_list = response;
                    this.wishlistSubject.next(
                        this.wishlist_private_list);
                    console.log(this.wishlist_private_list)
                }

            )
    }

    removeFromWishlist(playerID: string) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.delete(`http://localhost:5000/api/v1.0/users/${sessionStorage.user_id}/wishlist/${playerID}`, requestOptions).subscribe(response => {
            this.getWishlist()
            window.location.href = "/wishlist"
        })
    }

    getReviews(id: string, sort: string) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };
        return this.http.get(
            'http://localhost:5000/api/v1.0/players/' + id +
            '/reviews?sort=' + sort, requestOptions)
            .subscribe(
                response => {
                    this.reviews_private_list = response;
                    this.reviewsSubject.next(
                        this.reviews_private_list);
                    console.log(response)
                }
            )
    }

    postReview(review) {
        const headerDict = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': sessionStorage.token,
        }
        const requestOptions = {
            headers: new HttpHeaders(headerDict),
        };

        let postData = new FormData();
        postData.append("email", sessionStorage.email);
        postData.append("comment", review.review);
        console.log(sessionStorage.email + review.review)

        this.http.post(
            'http://localhost:5000/api/v1.0/players/' +
            this.playerID + '/reviews',
            postData).subscribe(
                response => {
                    this.getReviews(this.playerID, "recent");
                    console.log(response)
                });
    }
}