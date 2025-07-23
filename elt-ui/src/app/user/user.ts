import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';  // ✅ Import this

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user.html',
  styleUrls: ['./user.css'],
  standalone: true,
  imports: [RouterModule, CommonModule], // ✅ Add CommonModule here
})
export class UserDashboardComponent {
  coveragePercent: string = 'N/A';

  constructor(private http: HttpClient) {}

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
        const summary = res.totals?.percent_covered_display || "N/A";
        this.coveragePercent = summary;
        alert(`Test Coverage: ${summary}%`);
      },
      error: (err) => {
        console.error('Failed to load coverage report', err);
      }
    });
  }
}
