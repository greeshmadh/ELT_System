import { Component } from '@angular/core';
import { AuthService } from '../auth.service';
import { FormsModule } from '@angular/forms';  // ✅ This is required!
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  password = '';
  error = '';

  constructor(private auth: AuthService) {}

  onLogin() {
    this.auth.loginWithCredentials(this.username, this.password)
      .subscribe({
        next: () => {},
        error: () => {
          this.error = 'Invalid username or password';
        }
      });
  }
}
