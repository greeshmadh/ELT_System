import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders, HttpClientModule } from '@angular/common/http';

@Component({
  standalone: true,
  selector: 'app-data-view',
  imports: [CommonModule, HttpClientModule],
  templateUrl: './data-view-component.html'
})
export class DataViewComponent implements OnInit {
  columns: string[] = [];
  rows: any[] = [];
  error = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
  const data = localStorage.getItem('dataView');
  if (data) {
    const parsed = JSON.parse(data);
    this.columns = parsed.columns;
    this.rows = parsed.rows;
  } else {
    this.error = 'No data available. Please upload and view a YAML file first.';
  }
}
}
