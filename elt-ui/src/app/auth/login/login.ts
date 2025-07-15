import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';  // ✅ import this

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],  // ✅ required for ngModel to work
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login {
  token: string = '';  // ✅ required for ngModel
  role: 'admin' | 'user' = 'user';

  onLogin() {
    console.log('Logging in with:', this.token, this.role);
  }
}
