import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UserRoutingModule } from './user-routing-module';
import { User } from './user';


@NgModule({
  declarations: [
    User
  ],
  imports: [
    CommonModule,
    UserRoutingModule
  ]
})
export class UserModule { }
