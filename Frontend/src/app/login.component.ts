import { Component } from '@angular/core';
import { WebService } from './web.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})


export class LogInComponent {

    loginForm;
    credentials;
    submitError;


    constructor(public webService: WebService, private formBuilder: FormBuilder) { }

    ngOnInit() {
        this.loginForm = this.formBuilder.group({
            username: ['', [ Validators.required, Validators.email]],
            password: ['', [Validators.required,  Validators.minLength(8), Validators.maxLength(15)]],
        });
        if (sessionStorage.token) {
            window.location.href = "/"
        }
    }

    onSubmit() {
        if (this.isIncomplete()) {
            this.submitError = true
        }
        else {
            this.submitError = false
            this.webService.attemptLogin(this.loginForm.value);
            this.loginForm.reset();
        }
    }

    isInvalid(control) {
        return this.loginForm.controls[control].invalid &&
            this.loginForm.controls[control].touched;
    }

    isUnTouched() {
        return this.loginForm.controls.username.pristine ||
            this.loginForm.controls.password.pristine;
    }

    isIncomplete() {
        return this.isInvalid('username') ||
            this.isInvalid('password') ||
            this.isUnTouched();
    }

}