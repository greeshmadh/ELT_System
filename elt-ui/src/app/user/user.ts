import { Component, OnInit, Renderer2, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user.html',
  styleUrls: ['./user.css'],
  standalone: true,
  imports: [RouterModule, CommonModule],
})
export class UserDashboardComponent implements OnInit {
  coveragePercent: string = 'N/A';

  constructor(
    private http: HttpClient,
    private renderer: Renderer2,
    private el: ElementRef
  ) {}

  ngOnInit() {
    this.createParticles();
    this.setupMouseTracking();
  }

  // Your existing HTTP methods
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

    // Show loading animation
    this.showLoading();

    this.http.post<any>('http://localhost:5000/data-view', formData, { headers }).subscribe({
      next: (res) => {
        this.hideLoading();
        localStorage.setItem('dataView', JSON.stringify(res));
        window.location.href = '/data-view';
      },
      error: (err) => {
        this.hideLoading();
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

    // Show loading animation
    this.showLoading();

    this.http.get<any>('http://localhost:5000/coverage-report', { headers }).subscribe({
      next: (res) => {
        this.hideLoading();
        const summary = res.totals?.percent_covered_display || "N/A";
        this.coveragePercent = summary;
        
        // Animate coverage display if it's a number
        if (summary !== "N/A") {
          this.animateCoverageBar(parseFloat(summary));
        }
        
        alert(`Test Coverage: ${summary}%`);
      },
      error: (err) => {
        this.hideLoading();
        console.error('Failed to load coverage report', err);
      }
    });
  }

  // UI Animation Methods
  private createParticles() {
    const particlesContainer = this.el.nativeElement.querySelector('#particles');
    if (!particlesContainer) return;

    for (let i = 0; i < 20; i++) {
      const particle = this.renderer.createElement('div');
      this.renderer.addClass(particle, 'particle');
      
      // Random positioning
      this.renderer.setStyle(particle, 'left', Math.random() * 100 + '%');
      this.renderer.setStyle(particle, 'top', Math.random() * 100 + '%');
      this.renderer.setStyle(particle, 'animation-delay', Math.random() * 6 + 's');
      this.renderer.setStyle(particle, 'animation-duration', (Math.random() * 4 + 4) + 's');
      
      this.renderer.appendChild(particlesContainer, particle);
    }
  }

  private setupMouseTracking() {
    // Mouse tracking removed - static background only
  }

  private showLoading() {
    const loading = this.el.nativeElement.querySelector('#loading');
    if (loading) {
      this.renderer.setStyle(loading, 'display', 'block');
    }
  }

  private hideLoading() {
    const loading = this.el.nativeElement.querySelector('#loading');
    if (loading) {
      this.renderer.setStyle(loading, 'display', 'none');
    }
  }

  private animateCoverageBar(percent: number) {
    setTimeout(() => {
      const coverageFill = this.el.nativeElement.querySelector('.coverage-fill');
      if (coverageFill) {
        this.renderer.setStyle(coverageFill, 'width', percent + '%');
      }
    }, 500);
  }

  // Check if coverage is a valid number for progress bar display
  get isValidCoverage(): boolean {
    return this.coveragePercent !== 'N/A' && !isNaN(parseFloat(this.coveragePercent));
  }

  get coverageNumber(): number {
    return this.isValidCoverage ? parseFloat(this.coveragePercent) : 0;
  }
}