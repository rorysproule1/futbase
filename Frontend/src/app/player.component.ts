import { Component } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'player',
    templateUrl: './player.component.html',
    styleUrls: ['./player.component.css']
})

export class PlayerComponent {

    reviewForm;
    sort = "recent"

    constructor(public webService: WebService,
        private route: ActivatedRoute, private formBuilder: FormBuilder) { }

    ngOnInit() {
        // redirect to login if they arent authorised
        if (!sessionStorage.user_id) {
            window.location.href = "login"
        }
        this.reviewForm = this.formBuilder.group({
            review: [''],
        });
        this.webService.getPlayer(this.route.snapshot.params.id);
        this.webService.getReviews(this.route.snapshot.params.id, this.sort);
    }

    onSubmit() {
        this.webService.postReview(this.reviewForm.value);
        this.reviewForm.reset();
    }

    addToWishlist(base_id, player_id) {
        this.webService.postToWishlist(base_id, player_id)
    }

    downvote(review_id) {
        this.webService.downvoteReview(review_id, this.sort)
    }

    upvote(review_id) {
        this.webService.upvoteReview(review_id, this.sort)
    }

    sortReviews(sort_name) {
        this.sort = sort_name
        this.webService.getReviews(this.route.snapshot.params.id, this.sort)
    }

    // isInvalid(control) {
    //     return this.reviewForm.controls[control].invalid &&
    //         this.reviewForm.controls[control].touched;
    // }

    // isUnTouched() {
    //     return this.reviewForm.controls.name.pristine ||
    //         this.reviewForm.controls.review.pristine;
    // }

    // isIncomplete() {
    //     return this.isInvalid('name') ||
    //         this.isInvalid('review') ||
    //         this.isUnTouched();
    // }

}