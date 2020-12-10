import { Component } from '@angular/core';
import { WebService } from './web.service';

@Component({
    selector: 'businesses',
    templateUrl: './businesses.component.html',
    styleUrls: ['./businesses.component.css']
})


export class BusinessesComponent {
    constructor(public webService: WebService) { }

    ngOnInit() {
        if (sessionStorage.page) {
            this.page = sessionStorage.page;
        }
        this.webService.getBusinesses(this.page);
    }

    nextPage() {
        this.page = Number(this.page) + 1;
        sessionStorage.page = Number(this.page);
        this.webService.getBusinesses(this.page);
    }
    previousPage() {
        if (this.page > 1) {
            this.page = Number(this.page) - 1;
            sessionStorage.page = Number(this.page);
            this.webService.getBusinesses(this.page);
        }
    }


    page = 1;

}