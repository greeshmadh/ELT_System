// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { AuthGuard } from './auth/auth.guard';
import { AdminDashboardComponent } from './admin/admin-dashboard.component';
import { LogsComponent } from './logs/logs'; // make sure path is correct
import { TriggerJobComponent } from './triggerjob/triggerjob'; // make sure path is correct
import { DataViewComponent } from './data-view-component/data-view-component';
export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'user',
    canActivate: [AuthGuard],
    loadChildren: () => import('./user/user-module').then(m => m.UserModule)
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  {
  path: 'admin',
  component: AdminDashboardComponent,
  canActivate: [AuthGuard]
},
  {
  path: 'logs',
  loadComponent: () => import('./logs/logs').then(m => m.LogsComponent),
  canActivate: [AuthGuard]
},

  {
  path: 'admin/trigger',
  loadComponent: () => import('./triggerjob/triggerjob').then(m => m.TriggerJobComponent),
  canActivate: [AuthGuard]
},

{
  path: 'config-history',
  loadComponent: () => import('./confighist/confighist').then(m => m.ConfigHistoryComponent)
},
{
  path: 'data-view',
  loadComponent: () => import('./data-view-component/data-view-component').then(m => m.DataViewComponent),
}
 // ✅ Add this line

];




