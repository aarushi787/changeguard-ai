import React from 'react';
import {createRoot} from 'react-dom/client';
import {QueryClient,QueryClientProvider,useQuery} from '@tanstack/react-query';
import {IconShieldCheck,IconAlertTriangle} from '@tabler/icons-react';
import {api,ApiError,LoginScreen} from './drawing-workspace';
import Universal from './universal';
import './styles.css';
const client=new QueryClient({defaultOptions:{queries:{retry:false,refetchOnWindowFocus:false}}});
function App(){
 const me=useQuery({queryKey:['me'],queryFn:()=>api('/auth/me')});
 if(me.isPending)return <div className="loading-screen"><IconShieldCheck size={42}/><h2>ChangeGuard AI</h2><p>Loading your controlled change workspace…</p></div>;
 if(me.isError&&(!(me.error instanceof ApiError)||me.error.status!==401))return <div className="loading-screen" role="alert"><IconAlertTriangle size={42}/><h2>Workspace service unavailable</h2><p>We could not reach your workspace service. Free hosting may need a minute to wake.</p><button className="button primary" onClick={()=>me.refetch()}>Retry connection</button></div>;
 if(!me.data)return <LoginScreen onLogin={()=>window.location.reload()}/>;
 return <Universal me={me.data}/>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><QueryClientProvider client={client}><App/></QueryClientProvider></React.StrictMode>);
