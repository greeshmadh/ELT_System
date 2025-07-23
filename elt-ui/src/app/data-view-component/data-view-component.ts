import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';  // 🔑 Required for ngModel

@Component({
  standalone: true,
  selector: 'app-data-view',
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './data-view-component.html',
  styleUrls: ['./data-view-component.css'],
})
export class DataViewComponent implements OnInit {
  columns: string[] = [];
  rows: any[] = [];
  filteredRows: any[] = [];
  searchTerm: string = '';
  error = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    const data = localStorage.getItem('dataView');
    if (data) {
      const parsed = JSON.parse(data);
      this.columns = parsed.columns;
      this.rows = parsed.rows;
      this.filteredRows = this.rows; // ✅ Initialize filter
    } else {
      this.error = 'No data available. Please upload and view a YAML file first.';
    }
  }

  applyFilter() {
    const lowerSearch = this.searchTerm.toLowerCase();
    this.filteredRows = this.rows.filter(row =>
      this.columns.some(col =>
        String(row[col]).toLowerCase().includes(lowerSearch)
      )
    );
  }
}
