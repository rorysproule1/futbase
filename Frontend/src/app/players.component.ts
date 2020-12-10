import { Component } from '@angular/core';
import { WebService } from './web.service';

@Component({
    selector: 'players',
    templateUrl: './players.component.html',
    styleUrls: ['./players.component.css']
})


export class PlayersComponent {
    constructor(public webService: WebService) { }

    ngOnInit() {
        if (sessionStorage.page) {
            this.page = sessionStorage.page;
        }
        this.webService.getPlayers(this.page);
    }

    nextPage() {
        this.page = Number(this.page) + 1;
        sessionStorage.page = Number(this.page);
        this.webService.getPlayers(this.page);
    }
    previousPage() {
        if (this.page > 1) {
            this.page = Number(this.page) - 1;
            sessionStorage.page = Number(this.page);
            this.webService.getPlayers(this.page);
        }
    }


    page = 1;

}