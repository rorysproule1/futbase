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
import { SignUpComponent } from './signup.component';


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
// both my account and admin tools have not been implemented on the frontend due to time constraints,
// however they are both functional through the backend api. You can see the level of access in place 
// on the frontend as only admin users can see the admin tools option
{
  path: 'my-account',
  component: PlayersComponent
},
{
  path: 'admin-tools',
  component: PlayersComponent
},

{
  path: 'sign-up',
  component: SignUpComponent
},
];

@NgModule({
  declarations: [
    AppComponent, HomeComponent, NavComponent, PlayersComponent, PlayerComponent, LogInComponent, WishlistComponent, SignUpComponent
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
