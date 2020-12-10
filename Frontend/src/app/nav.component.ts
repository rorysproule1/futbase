import { Component } from '@angular/core';
import { AuthService } from './auth-service';

@Component({
 selector: 'navigation',
 templateUrl: './nav.component.html',
 styleUrls: []
})
export class NavComponent {
    constructor(public authService: AuthService) { }
 }