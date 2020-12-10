import { Component } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from './auth-service';

@Component({
    selector: 'business',
    templateUrl: './business.component.html',
    styleUrls: ['./business.component.css']
})

export class BusinessComponent {

    reviewForm;

    constructor(public webService: WebService,
        private route: ActivatedRoute, private formBuilder: FormBuilder, public authService: AuthService) {}

    ngOnInit() {
        this.reviewForm = this.formBuilder.group({
            name: ['', Validators.required],
            review: ['', Validators.required],
            stars: 5
        });
        this.webService.getBusiness(this.route.snapshot.params.id);
        this.webService.getReviews(this.route.snapshot.params.id);
    }

    onSubmit() {
        this.webService.postReview(this.reviewForm.value);
        this.reviewForm.reset();
    }

    isInvalid(control) {
        return this.reviewForm.controls[control].invalid &&
            this.reviewForm.controls[control].touched;
    }

    isUnTouched() {
        return this.reviewForm.controls.name.pristine ||
            this.reviewForm.controls.review.pristine;
    }

    isIncomplete() {
        return this.isInvalid('name') ||
            this.isInvalid('review') ||
            this.isUnTouched();
    }

}