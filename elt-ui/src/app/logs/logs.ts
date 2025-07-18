import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-logs',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './logs.html',
})
export class LogsComponent {
  logs: string[] = [];

  constructor(private http: HttpClient) {
    this.fetchLogs();
  }

  fetchLogs() {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('JWT token missing');
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get<any>('http://localhost:5000/logs', { headers }).subscribe({
      next: res => this.logs = res.logs,
      error: err => console.error('Error fetching logs:', err)
    });
  }
}
