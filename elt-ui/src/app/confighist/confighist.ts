import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-config-history',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './confighist.html',
})
export class ConfigHistoryComponent implements OnInit {
  configs: any[] = [];
  selectedConfig: any = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchConfigs();
  }

  fetchConfigs() {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('JWT token missing');
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get<any>('http://localhost:5000/config-history', { headers }).subscribe({
      next: res => this.configs = res.configs,
      error: err => console.error('Error fetching config history:', err)
    });
  }

  viewYaml(config: any) {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('JWT token missing');
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get<any>(`http://localhost:5000/config/${config.id}`, { headers }).subscribe({
      next: res => this.selectedConfig = res,
      error: err => console.error('Error fetching full config:', err)
    });
  }
}
