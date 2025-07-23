import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css'],
  standalone: true,
  imports: [RouterModule, CommonModule],
})
export class AdminDashboardComponent {
  coveragePercent: string | null = null;  // ✅ Add this to track coverage display

  constructor(private http: HttpClient) {}

  triggerJob(fileInput: HTMLInputElement) {
    const file = fileInput.files?.[0];
    if (!file) {
      alert("Please select a YAML file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    this.http.post('http://localhost:5000/trigger-job', formData).subscribe({
      next: (res: any) => alert(res.message || 'ELT Job triggered successfully!'),
      error: (err: any) => alert('Failed to trigger ELT job: ' + (err.error?.error || err.message))
    });
  }

  viewLogs() {
    window.location.href = '/logs';
  }

  viewHistory() {
    window.location.href = '/config-history';
  }

  viewData(fileInput: HTMLInputElement) {
    const file = fileInput.files?.[0];
    if (!file) {
      alert('Please select a YAML file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    if (!token) {
      alert('JWT token missing');
      return;
    }

    const headers = { Authorization: `Bearer ${token}` };

    this.http.post<any>('http://localhost:5000/data-view', formData, { headers }).subscribe({
      next: (res) => {
        localStorage.setItem('dataView', JSON.stringify(res));
        window.location.href = '/data-view';
      },
      error: (err) => {
        alert('Failed to load data view');
        console.error(err);
      }
    });
  }

  fetchCoverage() {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('JWT token missing');
      return;
    }

    const headers = { Authorization: `Bearer ${token}` };

    this.http.get<any>('http://localhost:5000/coverage-report', { headers }).subscribe({
      next: (res) => {
        const summary = res.totals?.percent_covered_display;
        this.coveragePercent = summary ?? "N/A";  // ✅ Fallback if undefined
        alert(`Test Coverage: ${this.coveragePercent}%`);
      },
      error: (err) => {
        console.error('Failed to load coverage report', err);
      }
    });
  }
}
