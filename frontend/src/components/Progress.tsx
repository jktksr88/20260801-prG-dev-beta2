import { useTranslation } from 'react-i18next'
export default function Progress({step,total}:{step:number;total:number}){const{t}=useTranslation();return <div className="progress-wrap"><div className="progress-copy"><span>{t('step')} {step}</span><span>{step}/{total}</span></div><div className="progress-track"><span style={{width:`${step/total*100}%`}}/></div></div>}
