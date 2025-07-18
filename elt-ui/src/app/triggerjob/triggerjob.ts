// src/app/triggerjob/triggerjob.component.ts
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-triggerjob',
  templateUrl: './triggerjob.html',
  styleUrls: ['./triggerjob.css']
})
export class TriggerJobComponent {
  selectedFile: File | null = null;
  message: string = '';

  constructor(private http: HttpClient) {}

  onFileSelected(event: Event) {
    const fileInput = event.target as HTMLInputElement;
    this.selectedFile = fileInput?.files?.[0] || null;
  }

  onUpload() {
    if (!this.selectedFile) {
      this.message = 'Please select a YAML file to upload.';
      return;
    }

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post('http://localhost:5000/trigger-job', formData)
      .subscribe({
        next: (res: any) => this.message = res.message,
        error: (err) => this.message = 'Upload failed: ' + err.error?.error || err.statusText
      });
  }
}
