import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AppComponent } from './app.component';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { HomeComponent } from './home.component';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthService } from "./auth-service";
import { NavComponent } from './nav.component';
import { PlayersComponent } from './players.component';
import { CommonModule } from '@angular/common';
import { PlayerComponent } from './player.component';
import { LogInComponent } from './login.component';
import { WishlistComponent } from './wishlist.component';


var routes = [{
  path: '',
  component: PlayersComponent
},
{
  path: 'login',
  component: LogInComponent
},
{
  path: 'players/:id',
  component: PlayerComponent
},
{
  path: 'wishlist',
  component: WishlistComponent
},
{
  path: 'admin-tools',
  component: PlayersComponent
},
];

@NgModule({
  declarations: [
    AppComponent, HomeComponent, NavComponent, PlayersComponent, PlayerComponent, LogInComponent, WishlistComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    ReactiveFormsModule,
    CommonModule,
  ],
  providers: [WebService, AuthService],
  bootstrap: [AppComponent]
})
export class AppModule { }
