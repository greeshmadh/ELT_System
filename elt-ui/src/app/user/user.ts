import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user.html',
  styleUrls: ['./user.css'],
  standalone: true,
  imports: [RouterModule],
})
export class UserDashboardComponent {
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
      // Save response to localStorage or a shared service if needed
      localStorage.setItem('dataView', JSON.stringify(res));
      window.location.href = '/data-view';
    },
    error: (err) => {
      alert('Failed to load data view');
      console.error(err);
    }
  });
}

}
export class User{}
