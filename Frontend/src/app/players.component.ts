import { Component } from '@angular/core';
import { WebService } from './web.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
    selector: 'players',
    templateUrl: './players.component.html',
    styleUrls: ['./players.component.css']
})


export class PlayersComponent {

    playersForm
    number_list = []
    position_list = ["ST", "CF", "RF", "LF", "LW", "RW", "CAM", "RM", "LM", "CM", "CDM", "LWB", "LB", "RWB", "RB", "CB", "GK"]
    quality_list = ["Gold - Rare", "Gold - Non-Rare", "Silver - Rare", "Silver - Non-Rare", "Bronze - Rare", "Bronze - Non-Rare"]
    // not a complete list of every revision as there are too many, just the main ones.
    revision_list = ["Normal", "CL", "IF", "Icon", "TOTY", "OTW", "POTM", "Halloween", "SBC", "Objectives"]
    page = 1;
    player_count = 0;
    total_pages = 0

    constructor(public webService: WebService, private formBuilder: FormBuilder) { }

    ngOnInit() {
        // redirect to login if they arent authorised
        if (!sessionStorage.user_id) {
            window.location.href = "login"
        }

        if (sessionStorage.page) {
            this.page = sessionStorage.page;
        }
        this.playersForm = this.formBuilder.group({
            name: [''],
            overall: [''],
            position: [''],
            nationality: [''],
            league: [''],
            club: [''],
            quality: [''],
            revision: [''],
        });
        this.webService.getPlayers(this.page, this.playersForm.value);
        this.number_list = Array(52).fill(0).map((x, i) => i + 48);
        this.number_list = this.number_list.reverse()
        this.page = 1
    }

    onSubmit() {
        this.webService.getPlayers(this.page, this.playersForm.value);
    }

    clear() {
        this.playersForm.reset();
        this.webService.getPlayers(1, this.playersForm.value)
        sessionStorage.page = 1
        window.location.reload()
    }

    nextPage() {
        this.page = Number(this.page) + 1;
        sessionStorage.page = Number(this.page);
        this.webService.getPlayers(this.page, this.playersForm.value);
    }
    previousPage() {
        if (this.page > 1) {
            this.page = Number(this.page) - 1;
            sessionStorage.page = Number(this.page);
            this.webService.getPlayers(this.page, this.playersForm.value);
        }
    }


}