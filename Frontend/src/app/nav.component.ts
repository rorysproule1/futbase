import { Component } from '@angular/core';
import { AuthService } from './auth-service';
import { WebService } from './web.service';

@Component({
    selector: 'navigation',
    templateUrl: './nav.component.html',
    styleUrls: []
})
export class NavComponent {
    constructor(public webService: WebService, public authService: AuthService) { }

    loggedIn;
    isAdmin

    ngOnInit() {
        if (sessionStorage.user_id) {
            this.loggedIn = true
            if (sessionStorage.admin === "true") {
                this.isAdmin = true
            }
            else {
                this.isAdmin = false
            }
        }
        else {
            this.loggedIn = false
        }
    }

    logout() {
        this.webService.logOut()
    }
}

