import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-logs',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './logs.html',
  styleUrls: ['./logs.css']
})
export class LogsComponent implements OnInit, OnDestroy {
  logs: string[] = [];
  private intervalId: any;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchLogs();  // Initial fetch
    this.intervalId = setInterval(() => this.fetchLogs(), 10000);
  }

  ngOnDestroy(): void {
    clearInterval(this.intervalId);  // Cleanup to avoid memory leaks
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
