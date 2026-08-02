import { useTranslation } from 'react-i18next'
import type { Language } from '../types'
export default function Header({language,onLanguage,onNavigate,onAuth,authenticated}:{language:Language;onLanguage:(l:Language)=>void;onNavigate:(v:string)=>void;onAuth:()=>void;authenticated:boolean}){
 const {t}=useTranslation()
 return <header className="site-header"><button className="brand" onClick={()=>onNavigate('landing')} aria-label="GROE home"><img src="/groe-mark.svg"/><span><b>GROE</b><small>{t('brandTag')}</small></span></button><nav><button onClick={()=>onNavigate('how')}>{t('navHow')}</button><button onClick={()=>onNavigate('gardens')}>{t('navGardens')}</button><button onClick={()=>onNavigate('plants')}>{t('navPlants')}</button></nav><div className="header-actions"><div className="lang-switch" aria-label="Language"><button className={language==='en'?'active':''} onClick={()=>onLanguage('en')}>EN</button><button className={language==='id'?'active':''} onClick={()=>onLanguage('id')}>ID</button></div><button className="button secondary compact" onClick={onAuth}>{authenticated?t('navGardens'):t('signIn')}</button></div></header>
}
