export type Language = 'en' | 'id'
export type Point = [number, number]
export interface PlannerInput {
  location: { city: string; latitude?: number; longitude?: number; elevation_m?: number }
  plot: { shape: 'rectangle'|'square'|'l_shape'|'custom'; length_m?: number; width_m?: number; points?: Point[]; entrance_edge?: number; sun_direction: 'north'|'east'|'south'|'west' }
  surface: 'soil'|'containers'|'mixed'
  sunlight: 'shade'|'partial'|'full'
  care_commitment: 'low'|'regular'|'hands_on'
  primary_goal: 'easy'|'fast'|'kitchen'|'variety'|'yield'
  desired_crops: string[]
  excluded_crops: string[]
  vertical_allowed: boolean
  tiered_rack_allowed: boolean
  water_access: 'limited'|'normal'|'easy'
  household_size?: number
  child_or_pet_concerns: boolean
  desired_quantity?: number
  container_depth_cm?: number
  language: Language
}
export interface CropSummary {
  id:string; slug:string; name_en:string; name_id:string; scientific_name:string; category:string; quantity:number; score:number; classification:string; reason_codes:string[]; adjustment_codes:string[]; hard_constraints:string[]; parameters:Record<string,unknown>; verification_status:string
}
export interface Placement { placement_id:string; crop_profile_id:string; slug:string; name_en:string; name_id:string; x_m:number; y_m:number; width_m:number; height_m:number; shape:string; trellis:boolean; tier:number|null; zone:string; spacing_m:number }
export interface Layout { plot_boundary:Point[]; usable_boundary:Point[]; plot_area_m2:number; usable_area_m2:number; access_zone:Point[]|null; placements:Placement[]; vertical_modules:Array<Record<string,unknown>>; compost:Record<string,unknown>|null; occupied_area_m2:number; adjustments:Array<Record<string,unknown>>; scale_unit:string; sun_direction:string }
export interface Plan { key:string; name_en:string; name_id:string; accent:string; proposition_en:string; proposition_id:string; feasibility_score:number; beginner_difficulty:string; crop_profile_count:number; total_plants:number; estimated_occupied_area_m2:number; containers_required:number; vertical_modules_required:number; weekly_care_minutes:number; expected_first_harvest_days:number|null; expected_harvest_pattern:string; why_it_fits:string; adjustments:string[]; trade_off:string; crops:CropSummary[]; layout:Layout }
export interface RecommendationResponse { input_summary:PlannerInput; environment:Record<string,unknown>; plot:{area_m2:number;usable_area_m2:number}; plans:Plan[]; requested_crop_review:Array<Record<string,unknown>>; engine_version:string; deterministic:boolean; data_version:string }
export interface SavedPlan { id:string; name:string; language:Language; planner_input?:PlannerInput; plan_data:Plan|RecommendationResponse; share_slug:string; is_public:boolean; created_at:string; updated_at:string }
export interface DiaryEntry { id:string;plan_id:string;crop_profile_id:string|null;map_zone:string|null;entry_date:string;growth_stage:string|null;entry_text:string;user_question:string|null;ai_response:string|null;concern_level:string;detected_topics:string[];recommended_next_action:string|null;follow_up_date:string|null }
