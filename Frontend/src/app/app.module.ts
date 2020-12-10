import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { BusinessesComponent } from './businesses.component';
import { AppComponent } from './app.component';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { HomeComponent } from './home.component';
import { BusinessComponent } from './business.component';
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
  path: 'businesses',
  component: BusinessesComponent
},
{
  path: 'businesses/:id',
  component: BusinessComponent
}
];

@NgModule({
  declarations: [
    AppComponent, BusinessesComponent, HomeComponent, BusinessComponent, NavComponent, PlayersComponent, PlayerComponent, LogInComponent, WishlistComponent
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
