import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Triggerjob } from './triggerjob';

describe('Triggerjob', () => {
  let component: Triggerjob;
  let fixture: ComponentFixture<Triggerjob>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Triggerjob]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Triggerjob);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
