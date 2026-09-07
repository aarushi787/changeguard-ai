import {useEffect,useState} from 'react';
export type WorkspaceRoute={page:string,id:string|null,tab:string};
const pages=['Dashboard','Changes','Compare','Impact map','Actions','Approvals','Domains','Reports','Knowledge','Settings','Drawings'];
function read():WorkspaceRoute{
 const hash=window.location.hash;
 if(hash==='#engineering')return {page:'Drawings',id:null,tab:'Summary'};
 try{
  const parts=hash.replace(/^#\/?/,'').split('/').map(decodeURIComponent);
  if(parts[0]==='changes'&&parts[1])return {page:'Changes',id:parts[1],tab:parts[2]||'Summary'};
  return {page:pages.find(p=>p.toLowerCase()===parts[0])||'Dashboard',id:null,tab:'Summary'};
 }catch{return {page:'Dashboard',id:null,tab:'Summary'}}
}
export function useWorkspaceRoute(){
 const [route,setRoute]=useState(read);
 useEffect(()=>{const changed=()=>setRoute(read());window.addEventListener('hashchange',changed);return()=>window.removeEventListener('hashchange',changed)},[]);
 function navigate(next:WorkspaceRoute){
  const hash=next.id?`#/changes/${encodeURIComponent(next.id)}/${encodeURIComponent(next.tab)}`:`#/${next.page.toLowerCase()}`;
  if(window.location.hash!==hash)window.location.hash=hash;
  setRoute(next);
 }
 return {route,navigate};
}
