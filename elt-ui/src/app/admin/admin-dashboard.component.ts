import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css'],
  standalone: true
})
export class AdminDashboardComponent {
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
      error: (err) => alert('Failed to trigger ELT job: ' + (err.error?.error || err.message))
    });
  }

  viewLogs() {
    window.location.href = '/logs';
  }

  viewHistory() {
    window.location.href = '/config-history';
  }
}
