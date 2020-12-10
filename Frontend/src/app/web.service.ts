import { HttpClient } from '@angular/common/http';
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

    private businesses_private_list;
    private businessesSubject = new Subject();
    businesses_list = this.businessesSubject.asObservable();

    private business_private_list;
    private businessSubject = new Subject();
    business_list = this.businessSubject.asObservable();

    businessID;
    playerID;


    constructor(private http: HttpClient) { }

    getPlayers(page: Number) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/players?pn=' + page
        ).subscribe(response => {
            this.players_private_list = response;
            this.playersSubject.next(
                this.players_private_list);
        });
    }

    getPlayer(id: string) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/players/' + id)
            .subscribe(response => {
                let player_array = [];
                player_array.push(response)
                this.player_private_list = player_array;
                this.playerSubject.next(
                    this.player_private_list);
                this.playerID = id;
            });
    }

    getBusinesses(page: Number) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/businesses?pn=' + page
        ).subscribe(response => {
            this.businesses_private_list = response;
            this.businessesSubject.next(
                this.businesses_private_list);
        });
    }

    getBusiness(id: string) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/businesses/' + id)
            .subscribe(response => {
                let business_array = [];
                business_array.push(response)
                this.business_private_list = business_array;
                this.businessSubject.next(
                    this.business_private_list);
                this.businessID = id;
            });
    }

    getWishlist(id: string) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/users/5fcfd10846c3bb971cf5e7e9/wishlist')
            .subscribe(
                response => {
                    this.wishlist_private_list = response;
                    this.wishlistSubject.next(
                        this.wishlist_private_list);
                    console.log(this.wishlist_private_list)
                }

            )
    }

    getReviews(id: string) {
        return this.http.get(
            'http://localhost:5000/api/v1.0/players/' + id +
            '/reviews')
            .subscribe(
                response => {
                    this.reviews_private_list = response;
                    this.reviewsSubject.next(
                        this.reviews_private_list);
                }

            )
    }

    postReview(review) {
        let postData = new FormData();
        postData.append("email", "rory.sproule@outlook.com");
        postData.append("comment", review.review);

        this.http.post(
            'http://localhost:5000/api/v1.0/players/' +
            this.playerID + '/reviews',
            postData).subscribe(
                response => {
                    this.getReviews(this.playerID);
                });
    }

    // postReview(review) {
    //     let postData = new FormData();
    //     postData.append("username", review.name);
    //     postData.append("comment", review.review);
    //     postData.append("stars", review.stars);

    //     // let today = new Date();
    //     // let todayDate = today.getFullYear() + "-" +
    //     //     today.getMonth() + "-" +
    //     //     today.getDate();
    //     // postData.append("date", todayDate);

    //     this.http.post(
    //         'http://localhost:5000/api/v1.0/businesses/' +
    //         this.businessID + '/reviews',
    //         postData).subscribe(
    //             response => {
    //                 this.getReviews(this.businessID);
    //             });

    // }
}