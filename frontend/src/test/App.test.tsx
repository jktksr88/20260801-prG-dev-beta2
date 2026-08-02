import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import '../i18n'
import App from '../App'
describe('GROE app',()=>{it('shows the primary planning action',()=>{render(<App/>);expect(screen.getAllByRole('button',{name:/plan my garden/i}).length).toBeGreaterThan(0)})})
