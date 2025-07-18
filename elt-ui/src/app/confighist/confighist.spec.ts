import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Confighist } from './confighist';

describe('Confighist', () => {
  let component: Confighist;
  let fixture: ComponentFixture<Confighist>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Confighist]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Confighist);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
