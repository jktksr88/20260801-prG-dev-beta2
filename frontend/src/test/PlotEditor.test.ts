import { describe, expect, it } from 'vitest'
import { polygonArea, selfIntersects } from '../components/PlotEditor'
describe('plot geometry helpers',()=>{
 it('calculates rectangle area',()=>expect(polygonArea([[0,0],[2,0],[2,1],[0,1]])).toBe(2))
 it('detects self intersections',()=>expect(selfIntersects([[0,0],[2,2],[0,2],[2,0]])).toBe(true))
})
