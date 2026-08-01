import type { PlannerInput, RecommendationResponse, SavedPlan, DiaryEntry } from '../types'
const BASE='/api/v1'
const TOKEN_KEY='groe.tokens'
export interface Tokens { access_token:string; refresh_token:string }
export const authStore={
  get():Tokens|null { try { return JSON.parse(localStorage.getItem(TOKEN_KEY)||'null') } catch { return null } },
  set(tokens:Tokens|null){ if(tokens)localStorage.setItem(TOKEN_KEY,JSON.stringify(tokens));else localStorage.removeItem(TOKEN_KEY) }
}
async function request<T>(path:string,options:RequestInit={},retry=true):Promise<T>{
  const tokens=authStore.get(); const headers=new Headers(options.headers)
  if(!headers.has('Content-Type') && options.body)headers.set('Content-Type','application/json')
  if(tokens)headers.set('Authorization',`Bearer ${tokens.access_token}`)
  const response=await fetch(`${BASE}${path}`,{...options,headers})
  if(response.status===401 && retry && tokens){
    const refreshed=await fetch(`${BASE}/auth/refresh`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:tokens.refresh_token})})
    if(refreshed.ok){ const next=await refreshed.json();authStore.set(next);return request<T>(path,options,false) }
    authStore.set(null)
  }
  if(!response.ok){ let detail='Request failed';try{const body=await response.json();detail=typeof body.detail==='string'?body.detail:JSON.stringify(body.detail)}catch{};throw new Error(detail) }
  if(response.status===204)return undefined as T
  return response.json()
}
export const api={
  recommendations:(input:PlannerInput)=>request<RecommendationResponse>('/planner/recommendations',{method:'POST',body:JSON.stringify(input)}),
  register:(email:string,password:string,preferred_language:string)=>request<Tokens>('/auth/register',{method:'POST',body:JSON.stringify({email,password,preferred_language})}),
  login:(email:string,password:string)=>request<Tokens>('/auth/login',{method:'POST',body:JSON.stringify({email,password})}),
  me:()=>request<{id:string;email:string;preferred_language:string}>('/auth/me'),
  savePlan:(payload:{name:string;language:string;planner_input:PlannerInput;plan_data:PlanLike;is_public:boolean})=>request<SavedPlan>('/plans',{method:'POST',body:JSON.stringify(payload)}),
  plans:()=>request<{items:SavedPlan[]}>('/plans'),
  updatePlan:(id:string,payload:Record<string,unknown>)=>request<SavedPlan>(`/plans/${id}`,{method:'PATCH',body:JSON.stringify(payload)}),
  deletePlan:(id:string)=>request<void>(`/plans/${id}`,{method:'DELETE'}),
  diary:(planId:string)=>request<DiaryEntry[]>(`/diary?plan_id=${encodeURIComponent(planId)}`),
  addDiary:(payload:Record<string,unknown>)=>request<DiaryEntry>('/diary',{method:'POST',body:JSON.stringify(payload)}),
  plants:()=>request<{items:Array<Record<string,unknown>>}>('/plants?page_size=50'),
  sharedPlan:(slug:string)=>request<SavedPlan>(`/public/plans/${encodeURIComponent(slug)}`),
  locationSearch:(q:string,language:string)=>request<{items:Array<{name:string;admin1?:string;latitude:number;longitude:number;elevation?:number}>}>(`/weather/locations?q=${encodeURIComponent(q)}&language=${language}`),
}
type PlanLike=Record<string,unknown>
