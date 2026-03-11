import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/Traffic \+ Parking Intelligence Console/i);
  expect(headingElement).toBeInTheDocument();
});
