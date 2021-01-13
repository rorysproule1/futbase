import { Component } from '@angular/core';
import { WebService } from './web.service';
import { ActivatedRoute } from '@angular/router';


@Component({
    selector: 'wishlist',
    templateUrl: './wishlist.component.html',
    styleUrls: ['./wishlist.component.css']
})

export class WishlistComponent {


    constructor(public webService: WebService,
        private route: ActivatedRoute) { }

    ngOnInit() {
        // redirect to login if they arent authorised
        if (!sessionStorage.user_id) {
            window.location.href = "login"
        }
        this.webService.getWishlist();
    }

    onRemove(playerID) {
        this.webService.removeFromWishlist(playerID);
    }

}