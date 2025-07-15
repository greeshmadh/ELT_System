import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'auth_token';
  private roleKey = 'user_role';

  constructor(private http: HttpClient, private router: Router) {}

  loginWithCredentials(username: string, password: string) {
    return this.http.post<any>('http://localhost:5000/auth/login', { username, password })
      .pipe(response => {
        response.subscribe(res => {
          localStorage.setItem(this.tokenKey, res.token);
          localStorage.setItem(this.roleKey, res.role);
          this.router.navigate([res.role === 'admin' ? '/admin' : '/user']);
        });
        return response;
      });
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getRole(): string | null {
    return localStorage.getItem(this.roleKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
