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
        this.webService.getWishlist(this.route.snapshot.params.id);
    }

}