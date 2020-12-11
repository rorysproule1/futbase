import { Component } from '@angular/core';
import { WebService } from './web.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'signup',
    templateUrl: './signup.component.html',
    styleUrls: ['./signup.component.css']
})


export class SignUpComponent {

    signupForm;
    credentials;
    submitError;


    constructor(public webService: WebService, private formBuilder: FormBuilder) { }

    ngOnInit() {
        this.signupForm = this.formBuilder.group({
            username: ['', [ Validators.required, Validators.email]],
            password: ['', [Validators.required,  Validators.minLength(8), Validators.maxLength(15)]],
        });
    }

    onSubmit() {
        if (this.isIncomplete()) {
            this.submitError = true
        }
        else {
            this.submitError = false
            this.webService.createUser(this.signupForm.value);
            this.signupForm.reset();
        }
    }

    isInvalid(control) {
        return this.signupForm.controls[control].invalid &&
            this.signupForm.controls[control].touched;
    }

    isUnTouched() {
        return this.signupForm.controls.username.pristine ||
            this.signupForm.controls.password.pristine;
    }

    isIncomplete() {
        return this.isInvalid('username') ||
            this.isInvalid('password') ||
            this.isUnTouched();
    }

    redirect() {
        window.location.href = "/login"
    }

}