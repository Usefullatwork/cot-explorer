var M=null, COT=[], cotF='alle', cotQ='';
var CATS={alle:'Alle',aksjer:'Aksjer',valuta:'Valuta',renter:'Renter',ravarer:'Ravarer',krypto:'Krypto',landbruk:'Landbruk',volatilitet:'Vol',annet:'Annet'};
var SI={'bull-strong':{i:'🟢',t:'Kjoeper sterkt'},'bull-mild':{i:'🟡',t:'Svakt bullish'},'neutral':{i:'⚪',t:'Noytral'},'bear-mild':{i:'🟠',t:'Svakt bearish'},'bear-strong':{i:'🔴',t:'Selger sterkt'}};

function fm(n){if(n==null)return'-';var a=Math.abs(n);if(a>=1e6)return(n>0?'':'-')+(a/1e6).toFixed(2)+'M';if(a>=1e3)return(n>0?'':'-')+(a/1e3).toFixed(1)+'K';return String(Math.round(n));}
function fp(n){return(n>0?'+':'')+n.toFixed(2)+'%';}
function cc(n){return n>0?'bull':n<0?'bear':'neutral';}
function fmtP(v){if(!v)return'-';return v>100?v.toFixed(2):v.toFixed(5);}
function sig(net,oi){if(!oi)return'neutral';var p=net/oi;if(p>.15)return'bull-strong';if(p>.04)return'bull-mild';if(p<-.15)return'bear-strong';if(p<-.04)return'bear-mild';return'neutral';}

document.querySelectorAll('.nt').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.nt').forEach(function(x){x.classList.remove('active');});
    document.querySelectorAll('.panel').forEach(function(x){x.classList.remove('active');});
    b.classList.add('active');
    document.getElementById('panel-'+b.dataset.tab).classList.add('active');
  });
});

function togIde(idx){
  var el=document.getElementById('tdet'+idx);
  if(!el)return;
  var open=el.classList.contains('open');
  document.querySelectorAll('.tdet').forEach(function(x){x.classList.remove('open');});
  if(!open)el.classList.add('open');
}

function renderTopbar(p){
  var items=[['VIX',p.VIX],['DXY',p.DXY],['S&P',p.SPX],['NAS',p.NAS100],['EUR/USD',p.EURUSD],['USD/JPY',p.USDJPY],['Brent',p.Brent],['Gull',p.Gold]];
  var h='';
  items.forEach(function(item){
    if(!item[1])return;
    var up=item[1].chg1d>=0;
    h+='<div class="ti"><span class="tn">'+item[0]+'</span><span>'+item[1].price+'</span><span class="tc '+(up?'up':'dn')+'">'+fp(item[1].chg1d)+'</span></div>';
  });
  document.getElementById('tbar').innerHTML=h;
}

function renderMakro(m){
  var sm=m.dollar_smile,vx=m.vix_regime,p=m.prices||{};
  var segs=[['venstre','al','Venstre','Krise/Risk-off','VIX>20'],['midten','am','Midten','Goldilocks','Fed kutter'],['hoyre','ar','Hoyre','Vekst/Inflasjon','Olje>$85']];
  var sh='';
  segs.forEach(function(s){sh+='<div class="sseg'+(sm.position===s[0]?' '+s[1]:'')+'"><div class="sp">'+s[2]+'</div><div class="sl2">'+s[3]+'</div><div class="sd">'+s[4]+'</div></div>';});
  document.getElementById('smile').innerHTML=sh;
  var bc=sm.usd_color==='bull'?'var(--bull)':'var(--bear)';
  document.getElementById('smileDesc').innerHTML='<strong style="color:'+bc+'">USD '+sm.usd_bias+'</strong> - '+sm.desc;
  var inp=sm.inputs;
  var hyTxt = inp.hy_stress ? 'JA ('+fp(inp.hy_chg5d||0)+')' : 'NEI ('+fp(inp.hy_chg5d||0)+')';
  var ycTxt = inp.yield_curve!=null ? (inp.yield_curve>0?'+':'')+inp.yield_curve.toFixed(2)+'%' : '-';
  var ycCol = inp.yield_curve==null?'neutral':inp.yield_curve<-0.3?'bear':inp.yield_curve<0.3?'warn':'bull';
  var si2=[
    ['VIX',        (inp.vix||0).toFixed(1),          inp.vix>25?'bear':inp.vix>20?'warn':'bull'],
    ['HY Stress',  hyTxt,                             inp.hy_stress?'bear':'bull'],
    ['Brent',      '$'+(inp.brent||0).toFixed(0),     inp.brent>85?'warn':'bull'],
    ['TIPS 5d',    fp(inp.tip_trend_5d||0),           inp.tip_trend_5d>0?'bull':'bear'],
    ['DXY 5d',     fp(inp.dxy_trend_5d||0),           inp.dxy_trend_5d>0?'bull':'bear'],
    ['10Y-3M',     ycTxt,                             ycCol],
    ['Kobber 5d',  fp(inp.copper_5d||0),              inp.copper_5d>0?'bull':'bear'],
    ['EM 5d',      fp(inp.em_5d||0),                  inp.em_5d>0?'bull':'bear'],
  ];
  var sih='';si2.forEach(function(x){sih+='<div class="sii"><div class="sil">'+x[0]+'</div><div class="siv '+x[2]+'">'+x[1]+'</div></div>';});
  document.getElementById('smileInp').innerHTML=sih;
  document.getElementById('vixDet').innerHTML='<div class="snum '+(vx.color||'')+'">'+((vx.value||0).toFixed(1))+'</div><div class="slabel" style="margin-top:4px;color:var(--'+(vx.color||'m')+')">'+vx.label+'</div>';
  document.getElementById('vbadge').textContent='VIX '+(vx.value||0).toFixed(1);
  document.getElementById('vbadge').className='vb '+(vx.regime||'normal');
  var riskOff=inp.vix>20||inp.hy_stress||(inp.yield_curve!=null&&inp.yield_curve<-0.3);
  document.getElementById('safeH').innerHTML=riskOff?'<strong style="color:var(--bear)">Risk-off aktiv</strong><br>Kjop: USD, XAU, CHF, JPY<br>Selg: NOK, AUD, NZD, CAD':'<strong style="color:var(--bull)">Normalt marked</strong><br>Carry: AUD, NZD, CAD, NOK';
  var ms=[['VIX',(p.VIX||{}).price,(p.VIX||{}).chg5d||0,(p.VIX||{}).chg5d>0?'bear':'bull'],['DXY',(p.DXY||{}).price,(p.DXY||{}).chg5d||0,(p.DXY||{}).chg5d>0?'bull':'bear'],['Brent',(p.Brent||{}).price,(p.Brent||{}).chg5d||0,'warn'],['Gull',(p.Gold||{}).price,(p.Gold||{}).chg5d||0,(p.Gold||{}).chg5d>0?'bull':'bear']];
  var msh='';
  ms.forEach(function(x){msh+='<div class="card"><div class="ct">'+x[0]+'</div><div class="snum">'+(x[1]?x[1].toFixed(x[1]>100?0:2):'-')+'</div><div class="slabel" style="margin-top:4px;color:var(--'+x[3]+')">'+fp(x[2])+' (5d)</div></div>';});
  document.getElementById('macroStats').innerHTML=msh;
  // Rente & kreditt-panel
  var mi=m.macro_indicators||{};
  var rc=[
    ['10Y rente',    mi.TNX  ? mi.TNX.price.toFixed(2)+'%'  : '-', inp.yield_curve!=null&&inp.yield_curve<0?'bear':'bull'],
    ['3M rente',     mi.IRX  ? mi.IRX.price.toFixed(2)+'%'  : '-', 'neutral'],
    ['Rentekurve',   ycTxt,                                          ycCol],
    ['HY (HYG) 5d',  mi.HYG  ? fp(mi.HYG.chg5d)             : '-', mi.HYG&&mi.HYG.chg5d<-1.5?'bear':mi.HYG&&mi.HYG.chg5d<0?'warn':'bull'],
    ['TIPS 5d',      mi.TIP  ? fp(mi.TIP.chg5d)              : '-', mi.TIP&&mi.TIP.chg5d>0?'bull':'bear'],
    ['Kobber 5d',    mi.Copper? fp(mi.Copper.chg5d)          : '-', mi.Copper&&mi.Copper.chg5d>0?'bull':'bear'],
    ['EM (EEM) 5d',  mi.EEM  ? fp(mi.EEM.chg5d)              : '-', mi.EEM&&mi.EEM.chg5d>0?'bull':'bear'],
  ];
  var rch='';
  rc.forEach(function(x){rch+='<div class="card"><div class="ct">'+x[0]+'</div><div class="snum" style="font-size:20px">'+x[1]+'</div><div class="slabel" style="margin-top:4px;color:var(--'+x[2]+')">'+x[2].toUpperCase()+'</div></div>';});
  document.getElementById('macroRente').innerHTML=rch;
  document.getElementById('upd').textContent='Oppdatert: '+m.date;
}

function weightBadge(w){
  // Viser styrke-badge basert på tidsvindus-vekt
  if(!w) return '';
  var label = w>=5?'Ukentlig': w>=4?'PDH/PDL': w>=3?'D1': w>=2?'4H/SMC': '15m';
  var cls   = w>=4?'bull': w>=3?'warn': 'neutral';
  return '<span class="tf-badge '+cls+'">'+label+'</span>';
}

function renderSetupSide(setup, type){
  if(!setup){
    return '<div class="setup-label na">'+type+'</div><div style="color:var(--m);font-size:12px;padding:20px 0;text-align:center">Ikke tilgjengelig</div>';
  }
  var col=type==='LONG'?'bull':'bear';
  var rrOk=setup.rr_t1>=setup.min_rr;
  var distOk=setup.entry_dist_atr<=1.0;
  var entryW=setup.entry_weight||1;
  var t1W=setup.t1_weight||1;
  return '<div class="setup-label '+col+'">'+type+' – '+setup.entry_name+' '+weightBadge(entryW)+'</div>'+
    '<div class="setup-row"><span class="setup-key">Entry</span><span class="setup-val '+(distOk?col:'warn')+'">'+fmtP(setup.entry)+(distOk?' *':' ('+setup.entry_dist_atr+'xATR)')+'</span></div>'+
    '<div class="setup-row"><span class="setup-key">Stop Loss</span><span class="setup-val bear">'+fmtP(setup.sl)+'<span style="font-size:10px;color:var(--m);margin-left:6px">'+(setup.sl_type||'')+(setup.risk_atr_d?' · '+setup.risk_atr_d+'×ATRd':'')+'</span></span></div>'+
    '<div class="setup-row"><span class="setup-key">Target 1</span><span class="setup-val bull">'+fmtP(setup.t1)+' '+weightBadge(t1W)+(setup.t1_quality==='weak'?'<span class="tf-badge neutral" title="Svak T1 – ingen D1/4H-nivå funnet">?</span>':'')+'</span></div>'+
    '<div class="setup-row"><span class="setup-key">Target 2</span><span class="setup-val bull">'+fmtP(setup.t2)+'</span></div>'+
    '<div class="setup-row"><span class="setup-key">R:R T1</span><span class="rr-badge '+(rrOk?'ok':'bad')+'">1:'+setup.rr_t1+'</span></div>'+
    '<div class="setup-row"><span class="setup-key">R:R T2</span><span class="setup-val">1:'+setup.rr_t2+'</span></div>'+
    '<div class="setup-row"><span class="setup-key">Min R:R</span><span class="setup-val">1:'+setup.min_rr+'</span></div>'+
    '<div style="font-size:11px;color:var(--m);margin-top:8px">'+setup.note+'</div>';
}

function renderIdeer(m){
  var lvs=m.trading_levels||{};
  var arr=Object.values(lvs);
  document.getElementById('ideDate').textContent='COT per '+(m.cot_date||'-');
  var vr=m.vix_regime||{};
  var vsEl=document.getElementById('vixSize');
  vsEl.textContent=vr.label||'-';
  vsEl.style.color='var(--'+(vr.color||'m')+')';

  var aplus=arr.filter(function(l){return l.grade==='A+';}).length;
  var bgrade=arr.filter(function(l){return l.grade==='B';}).length;
  var active=arr.filter(function(l){return l.session&&l.session.active&&!l.binary_risk.length&&l.grade!=='C';}).length;
  var risk=arr.filter(function(l){return l.binary_risk&&l.binary_risk.length>0;}).length;
  var makro=arr.filter(function(l){return l.timeframe_bias==='MAKRO';}).length;

  document.getElementById('ideStats').innerHTML=
    '<div class="card"><div class="ct">A+ Setups</div><div class="snum bull">'+aplus+'</div><div class="slabel">Score 7-8/8</div></div>'+
    '<div class="card"><div class="ct">B Setups</div><div class="snum warn">'+bgrade+'</div><div class="slabel">Score 4-5/8</div></div>'+
    '<div class="card"><div class="ct">MAKRO Setups</div><div class="snum bull">'+makro+'</div><div class="slabel">COT + HTF struktur</div></div>'+
    '<div class="card"><div class="ct">Binar risiko</div><div class="snum bear">'+risk+'</div><div class="slabel">High impact neste 4t</div></div>';

  if(!arr.length){document.getElementById('ideGrid').innerHTML='<div class="loading">Ingen data – kjor fetch_all.py</div>';return;}

  arr.sort(function(a,b){
    var ga={'A+':-1,'A':0,'B':1,'C':2};
    var tf={'MAKRO':-1,'SWING':0,'SCALP':1,'WATCHLIST':2};
    var gd=(ga[a.grade]!==undefined?ga[a.grade]:2)-(ga[b.grade]!==undefined?ga[b.grade]:2);
    if(gd!==0)return gd;
    var td=(tf[a.timeframe_bias]||0)-(tf[b.timeframe_bias]||0);
    if(td!==0)return td;
    return (b.score||0)-(a.score||0);
  });

  var html='';
  arr.forEach(function(lv,i){
    var cot=lv.cot||{};
    var gc=lv.grade_color||'neutral';
    var sess=lv.session||{};
    var brisk=lv.binary_risk||[];
    var clsLv=lv.class||'A';
    var curr=lv.current||0;
    var specNet=cot.net||0;
    var pct=Math.min(100,Math.max(0,50+(specNet/Math.max(1,lv.open_interest||1e6))*50));
    var res=lv.resistances||[];
    var sup=lv.supports||[];
    var smaPos=lv.sma200_pos==='over';
    var smaFmt=lv.sma200?fmtP(lv.sma200):'-';
    var atrFmt=lv.atr14?(lv.atr14>10?lv.atr14.toFixed(1):lv.atr14.toFixed(5)):'-';
    var biasText=lv.dir_color==='bull'?'LONG':lv.dir_color==='bear'?'SHORT':'NOYTRAL';
    var tf=lv.timeframe_bias||'WATCHLIST';
    var tfCol=tf==='MAKRO'?'bull':tf==='SWING'?'warn':tf==='SCALP'?'neutral':'bear';

    function makeLR(l,type){
      var act=l.dist_atr<=1.0;
      var cls=act?(type==='res'?'ar':'as'):'';
      var lvlF=l.level>100?l.level.toFixed(1):l.level.toFixed(5);
      return '<div class="lr '+cls+'"><span class="ln">'+l.name+(act?' *':'')+' '+weightBadge(l.weight||1)+'</span><span><span class="lv">'+lvlF+'</span> <span class="ld">'+l.dist_atr.toFixed(1)+'x</span></span></div>';
    }
    var resH=res.slice(0,3).map(function(l){return makeLR(l,'res');}).join('');
    var supH=sup.slice(0,3).map(function(l){return makeLR(l,'sup');}).join('');

    // Score dots
    var scoreDots='';
    (lv.score_details||[]).forEach(function(sd){
      scoreDots+='<div class="score-item"><div class="score-dot" style="background:'+(sd.verdi?'var(--bull)':'var(--b2)')+'"></div>'+sd.kryss+'</div>';
    });

    // Binary risk warning
    var briskHtml='';
    if(brisk.length){
      var titles=brisk.map(function(r){return r.title;}).join(', ');
      briskHtml='<div class="binrisk">⚠️ Binar risiko: '+titles+'</div>';
    }

    html+=
      '<div class="tic">'+
        '<div class="tic-head" onclick="togIde('+i+')">'+
          '<span class="tcls">'+clsLv+'</span>'+
          '<div><div class="tname">'+lv.name+'</div><div class="tsub">'+(lv.label||'')+'</div></div>'+
          '<span class="tgrade '+gc+'">'+lv.grade+' '+lv.score+'/8</span>'+
          '<span class="tgrade '+tfCol+'">'+tf+'</span>'+
          '<span class="tbias '+(lv.dir_color||'neutral')+'">'+biasText+'</span>'+
          '<span class="tprice">'+fmtP(curr)+'</span>'+
          '<span class="tsess '+(sess.active?'active':'inactive')+'">'+(sess.active?'AKTIV SESJON':sess.label||'Utenfor sesjon')+'</span>'+
          (brisk.length?'<span class="trisk">⚠️ BINAR RISIKO</span>':'')+
        '</div>'+
        '<div id="tdet'+i+'" class="tdet">'+
          briskHtml+
          '<div class="setup-grid">'+
            '<div class="setup-side">'+renderSetupSide(lv.setup_long,'LONG')+'</div>'+
            '<div class="setup-side">'+renderSetupSide(lv.setup_short,'SHORT')+'</div>'+
          '</div>'+
          '<div class="score-section">'+
            '<div class="ct">Konfluens-score ('+lv.score_pct+'%)</div>'+
            '<div class="score-bar-wrap"><div class="score-bar"><div class="score-fill" style="width:'+lv.score_pct+'%;background:'+(gc==='bull'?'var(--bull)':gc==='warn'?'var(--warn)':'var(--bear)')+'"></div></div></div>'+
            '<div class="score-items">'+scoreDots+'</div>'+
          '</div>'+
          '<div class="levels-section">'+
            '<div><div class="lgt">Motstand</div>'+resH+'</div>'+
            '<div>'+
              '<div class="pline"><span class="pcurr">'+fmtP(curr)+'</span><span class="pm">Napris</span><span class="psma '+(smaPos?'above':'below')+'">SMA200 '+(smaPos?'Over':'Under')+'</span></div>'+
              '<div style="margin-top:8px"><div class="lgt">Stotte</div>'+supH+'</div>'+
            '</div>'+
            '<div><div class="lgt">Nokkeltall</div>'+
              '<div class="lr"><span class="ln">SMA200</span><span class="lv">'+smaFmt+'</span></div>'+
              '<div class="lr"><span class="ln">ATR14</span><span class="lv">'+atrFmt+'</span></div>'+
              '<div class="lr"><span class="ln">5d</span><span class="lv '+cc(lv.chg5d||0)+'">'+fp(lv.chg5d||0)+'</span></div>'+
              '<div class="lr"><span class="ln">20d</span><span class="lv '+cc(lv.chg20d||0)+'">'+fp(lv.chg20d||0)+'</span></div>'+
            '</div>'+
          '</div>'+
          '<div class="tmeta">'+
            '<div><div class="ml">COT Bias</div><div class="mv '+(cot.color||'neutral')+'">'+(cot.bias||'-')+'</div></div>'+
            '<div><div class="ml">COT Trend</div><div class="mv '+(cot.momentum==='ØKER'?'bull':cot.momentum==='SNUR'?'warn':'neutral')+'">'+(cot.momentum||'-')+'</div></div>'+
            '<div><div class="ml">DXY</div><div class="mv '+(lv.dxy_conf==='medvind'?'bull':'bear')+'">'+(lv.dxy_conf||'-')+'</div></div>'+
            '<div><div class="ml">Posisjon</div><div class="mv warn">'+(lv.pos_size||'-')+'</div></div>'+
            '<div><div class="ml">Spread-faktor</div><div class="mv">'+(lv.vix_spread_factor||'-')+'x</div></div>'+
          '</div>'+
          '<div class="tcotbar">'+
            '<div class="ct">COT Spekulanter ('+(cot.report||'-')+' per '+(cot.date||'-')+')</div>'+
            '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px">'+
              '<span>Netto: <strong class="'+(cot.color||'neutral')+'" style="font-family:monospace">'+(specNet>0?'+':'')+fm(specNet)+'</strong></span>'+
              '<span>Uke: <strong class="'+cc(cot.chg||0)+'" style="font-family:monospace">'+(cot.chg>0?'+':'')+fm(cot.chg||0)+'</strong></span>'+
              '<span>OI: <strong style="font-family:monospace">'+((cot.pct||0).toFixed(1))+'%</strong></span>'+
            '</div>'+
            '<div class="cbt"><div class="cbf" style="width:'+pct+'%;background:'+(specNet>0?'var(--bull)':'var(--bear)')+'"></div></div>'+
          '</div>'+
        '</div>'+
      '</div>';
  });
  document.getElementById('ideGrid').innerHTML=html;
}

function renderCot(){
  var data=COT.filter(function(d){
    if(cotF!=='alle'&&d.kategori!==cotF)return false;
    if(!cotQ)return true;
    return(d.navn_no+d.market+d.symbol+d.kategori).toLowerCase().indexOf(cotQ)>=0;
  });
  document.getElementById('cotCnt').textContent=data.length+' markeder';
  var counts={alle:COT.length};
  COT.forEach(function(d){counts[d.kategori]=(counts[d.kategori]||0)+1;});
  var fch='';
  Object.entries(CATS).forEach(function(entry){
    var k=entry[0],v=entry[1];
    if(k!=='alle'&&!counts[k])return;
    fch+='<button class="fc'+(k===cotF?' on':'')+'" onclick="setCF(\''+k+'\')">'+v+' <span style="opacity:.6">'+(counts[k]||0)+'</span></button>';
  });
  document.getElementById('fchips').innerHTML=fch;
  if(!data.length){document.getElementById('cotGrid').innerHTML='<div class="loading">Ingen resultater</div>';return;}
  var rows='';
  data.forEach(function(d){
    var sp=d.spekulanter||{};
    var s2=sig(sp.net||0,d.open_interest||1);
    var si=SI[s2];
    rows+='<tr><td style="cursor:pointer" onclick="openCotChart(\''+d.symbol+'\',\''+d.report+'\',\''+encodeURIComponent(d.navn_no||d.market)+'\')" ><div class="tdname">'+(d.navn_no||d.market)+'</div><div class="tdsub">'+(d.forklaring||'')+'</div></td>'+
      '<td><span class="sp2 '+s2+'">'+si.i+' '+si.t+'</span></td>'+
      '<td class="'+(sp.net>=0?'tdbull':'tdbear')+'">'+(sp.net>0?'+':'')+fm(sp.net||0)+'</td>'+
      '<td class="'+(d.change_spec_net>=0?'tdbull':'tdbear')+'">'+(d.change_spec_net>0?'+':'')+fm(d.change_spec_net||0)+'</td>'+
      '<td class="tdr">'+fm(d.open_interest||0)+'</td>'+
      '<td class="tdr" style="font-size:10px;color:var(--m)">'+d.report+'</td></tr>';
  });
  document.getElementById('cotGrid').innerHTML='<div class="cotw"><table class="cott"><thead><tr><th>Marked</th><th>Signal</th><th style="text-align:right">Spec. Netto</th><th style="text-align:right">Uke</th><th style="text-align:right">OI</th><th style="text-align:right">Kilde</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
}
function setCF(c){cotF=c;renderCot();}
function filterCot(){cotQ=document.getElementById('cotS').value.toLowerCase();renderCot();}

function renderCal(cal){
  var h=cal.filter(function(e){return e.impact==='High';});
  var m2=cal.filter(function(e){return e.impact==='Medium';});
  function ev(es){
    if(!es.length)return'<div style="color:var(--m);font-size:13px;padding:10px 0">Ingen</div>';
    return es.map(function(e){
      var dt=new Date(e.date);
      var t=dt.toLocaleString('nb-NO',{weekday:'short',hour:'2-digit',minute:'2-digit'});
      return'<div class="cali"><div class="calt">'+t+'</div><div><div class="calti">'+e.title+'</div><div class="calcc">'+e.country+' – Forecast: '+(e.forecast||'-')+'</div></div><span class="calimp '+e.impact+'">'+e.impact+'</span></div>';
    }).join('');
  }
  document.getElementById('calH').innerHTML=ev(h);
  document.getElementById('calM').innerHTML=ev(m2);
}

function renderPrices(p){
  var grps=[
    ['pInd',[['S&P 500','SPX'],['Nasdaq','NAS100'],['VIX','VIX'],['Gull','Gold'],['Solv','Silver']]],
    ['pVal',[['EUR/USD','EURUSD'],['USD/JPY','USDJPY'],['GBP/USD','GBPUSD'],['USD/CHF','USDCHF'],['AUD/USD','AUDUSD'],['DXY','DXY'],['USD/NOK','USDNOK']]],
    ['pRav',[['Brent','Brent'],['WTI','WTI'],['HYG','HYG'],['TIP','TIP']]]
  ];
  grps.forEach(function(grp){
    var html='';
    grp[1].forEach(function(item){
      var v=p[item[1]];if(!v)return;
      var up=v.chg1d>=0;
      html+='<div class="pc2"><div class="pcn">'+item[0]+'</div><div class="pcp">'+v.price+'</div><div class="pcc '+(up?'up':'dn')+'">'+fp(v.chg1d)+' 5d:'+fp(v.chg5d)+'</div></div>';
    });
    document.getElementById(grp[0]).innerHTML=html;
  });
}

async function loadAll(){
  try{
    var r=await fetch('data/macro/latest.json');
    M=await r.json();
    renderTopbar(M.prices||{});
    renderMakro(M);
    renderIdeer(M);
    renderCal(M.calendar||[]);
    renderPrices(M.prices||{});
  }catch(e){
    document.getElementById('ideGrid').innerHTML='<div class="loading">Kjor fetch_all.py og push til GitHub</div>';
    console.error(e);
  }
  try{
    var r2=await fetch('data/combined/latest.json');
    COT=await r2.json();
    renderCot();
  }catch(e){console.error(e);}
}
loadAll();

var cotChartInst = null;

function closeCotModal(e){
  if(e.target===document.getElementById('cotModal'))
    document.getElementById('cotModal').classList.remove('open');
}

var COT_PRICE_MAP = {};
fetch('data/prices/cot_map.json').then(function(r){return r.json();}).then(function(d){COT_PRICE_MAP=d;}).catch(function(){});
var YAHOO_MAP = {
  '099741': 'EURUSD=X',
  '096742': 'JPY=X',
  '096742': 'JPY=X',
  '092741': 'GBPUSD=X',
  '232741': 'AUDUSD=X',
  '090741': 'USDCHF=X',
  '088691': 'GC=F',
  '084691': 'SI=F',
  '067651': 'CL=F',
  '023651': 'BZ=F',
  '133741': '^GSPC',
  '209742': '^NDX',
  '095741': '^VIX',
  '098662': 'DX-Y.NYB',
  '002602': 'ZC=F',
  '001602': 'ZW=F',
  '005602': 'ZS=F',
  '083731': 'SB=F',
  '073732': 'KC=F',
  '080732': 'CC=F',
};

async function fetchYahooPrices(priceKey, startDate, endDate) {
  try {
    var r = await fetch("data/prices/" + priceKey + ".json");
    if(!r.ok) return [];
    var d = await r.json();
    return d.data||[];
  } catch(e) { return []; }
}

async function openCotChart(symbol, report, navn){
  var modal = document.getElementById('cotModal');
  navn = decodeURIComponent(navn);
  document.getElementById('cotModalTitle').textContent = navn + ' – COT Historikk';
  document.getElementById('cotModalStats').innerHTML = '<div style="color:var(--m);font-size:13px">Laster...</div>';
  modal.classList.add('open');

  var fname = symbol.toLowerCase() + '_' + report.toLowerCase() + '.json';
  var url   = 'data/timeseries/' + fname;

  try {
    var r  = await fetch(url);
    if(!r.ok) throw new Error('Ikke funnet');
    var ts = await r.json();
    var data = (ts.data||[]).filter(function(d){return d.date && d.spec_net!=null;});
    if(!data.length) throw new Error('Ingen data');

    var labels = data.map(function(d){return d.date;});
    var nets   = data.map(function(d){return d.spec_net;});
    var ois    = data.map(function(d){return d.oi||0;});

    // Farger: grønn over 0, rød under
    var barColors = nets.map(function(n){
      return n >= 0 ? 'rgba(0,200,100,0.7)' : 'rgba(255,80,80,0.7)';
    });

    if(cotChartInst) cotChartInst.destroy();

    // Hent prisdata hvis Yahoo-mapping finnes
    var yahooSym = YAHOO_MAP[symbol] || null;
  var priceKey  = COT_PRICE_MAP[symbol] || null;
  console.log('symbol:', symbol, 'priceKey:', priceKey, 'COT_PRICE_MAP:', JSON.stringify(COT_PRICE_MAP));
    var prices   = [];
    if(priceKey && data.length > 1) {
      prices = await fetchYahooPrices(priceKey, data[0].date, data[data.length-1].date);
    }

    // Bruk prisdata direkte med egne datoer
    var priceLabels = prices.map(function(p){ return p.date; });
    var priceData   = prices.map(function(p){ return p.price; });
    var hasPrices   = prices.length > 0;

    // Vis/skjul priceWrap
    var priceWrap = document.getElementById('priceWrap');
    if(hasPrices){
      priceWrap.style.display = 'block';
      document.getElementById('cotChart').style.height = '200px';
    } else {
      priceWrap.style.display = 'none';
      document.getElementById('cotChart').style.height = '300px';
    }

    var ctx = document.getElementById('cotChart').getContext('2d');
    cotChartInst = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Spec. Netto',
          data: nets,
          backgroundColor: barColors,
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {display:false},
          tooltip: {
            callbacks: {
              label: function(ctx){
                var v=ctx.raw;
                return (v>0?'+':'')+Math.round(v).toLocaleString();
              }
            }
          }
        },
        scales: {
          x: {ticks:{maxTicksLimit:10,color:'var(--m)',font:{size:10},maxRotation:0},grid:{color:'var(--b)'}},
          y: {
            ticks:{color:'var(--m)',font:{size:10},callback:function(v){
              if(Math.abs(v)>=1e6)return(v/1e6).toFixed(1)+'M';
              if(Math.abs(v)>=1e3)return(v/1e3).toFixed(0)+'K';
              return v;
            }},
            grid:{color:'var(--b)'}
          }
        }
      }
    });

    // Prisgraf
    if(hasPrices){
      var priceCanvas = document.getElementById('priceChart');
      if(window.priceChartInst) window.priceChartInst.destroy();
      var ctx2 = priceCanvas.getContext('2d');
      window.priceChartInst = new Chart(ctx2, {
        type: 'line',
        data: {
          labels: priceLabels,
          datasets:[{
            label: yahooSym,
            data: priceData,
            borderColor: 'rgba(255,255,255,0.8)',
            backgroundColor: 'rgba(255,255,255,0.05)',
            borderWidth: 1.5,
            pointRadius: 0,
            fill: true,
            tension: 0.3,
          }]
        },
        options:{
          responsive:true,
          maintainAspectRatio:false,
          plugins:{
            legend:{display:false},
            tooltip:{
              callbacks:{
                label:function(ctx){
                  var v=ctx.raw;
                  return v!=null?v.toFixed(v>100?2:4):'-';
                }
              }
            }
          },
          scales:{
            x:{ticks:{maxTicksLimit:10,color:'var(--m)',font:{size:10},maxRotation:0},grid:{color:'var(--b)'}},
            y:{ticks:{color:'var(--m)',font:{size:10}},grid:{color:'var(--b)'}}
          }
        }
      });

      // Legg til forklaring
      var inner = document.querySelector('.cot-modal-inner');
      var existing = inner.querySelector('.cot-explain');
      if(existing) existing.remove();
      var exp = document.createElement('div');
      exp.className = 'cot-explain';
      exp.style.cssText = 'font-size:12px;color:var(--m);margin-top:12px;padding:10px 12px;background:var(--s2);border-radius:6px;border:1px solid var(--b);line-height:1.6';
      var lastNet = nets[nets.length-1];
      var prevNet = nets[nets.length-2]||0;
      var trend   = lastNet > prevNet ? 'øker' : 'reduserer';
      var bias    = lastNet > 0 ? 'LONG (bullish)' : 'SHORT (bearish)';
      var extreme = Math.abs(lastNet) > Math.max.apply(null,nets.map(Math.abs))*0.8;
      var extTxt  = extreme ? ' ⚠️ Posisjonering nær historisk ekstrem — reverseringsrisiko.' : '';
      exp.innerHTML =
        '<strong>Hva betyr dette?</strong><br>'+
        'Søylene viser netto spekulant-posisjon (Managed Money / Non-Commercial). '+
        'Grønt = netto long (forventer oppgang), rødt = netto short (forventer fall).<br><br>'+
        'Nå er spekulanter <strong>'+bias+'</strong> og '+trend+' posisjonen sin.'+extTxt+'<br><br>'+
        'Prislinjen under viser hva som faktisk skjedde med '+yahooSym+' i samme periode. '+
        'Når COT og pris beveger seg likt = spekulanter har rett. Når de divergerer = mulig vending.';
      inner.querySelector('.cot-stat-row').after(exp);
    }

    // Stats
    var last  = nets[nets.length-1];
    var prev  = nets[nets.length-2]||0;
    var chg   = last - prev;
    var max   = Math.max.apply(null, nets);
    var min   = Math.min.apply(null, nets);
    var pct   = ois[ois.length-1] ? (last/ois[ois.length-1]*100).toFixed(1) : '-';
    function fm(n){if(n==null)return'-';var a=Math.abs(n);if(a>=1e6)return(n>0?'':'-')+(a/1e6).toFixed(2)+'M';if(a>=1e3)return(n>0?'':'-')+(a/1e3).toFixed(1)+'K';return(n>0?'':'')+Math.round(n);}
    function cc(n){return n>0?'bull':n<0?'bear':'neutral';}

    document.getElementById('cotModalStats').innerHTML =
      '<div class="cot-stat"><div class="cot-stat-label">Netto nå</div><div class="cot-stat-val '+cc(last)+'">'+fm(last)+'</div></div>'+
      '<div class="cot-stat"><div class="cot-stat-label">Uke endring</div><div class="cot-stat-val '+cc(chg)+'">'+fm(chg)+'</div></div>'+
      '<div class="cot-stat"><div class="cot-stat-label">% av OI</div><div class="cot-stat-val">'+pct+'%</div></div>'+
      '<div class="cot-stat"><div class="cot-stat-label">Historisk maks</div><div class="cot-stat-val bull">'+fm(max)+'</div></div>'+
      '<div class="cot-stat"><div class="cot-stat-label">Historisk min</div><div class="cot-stat-val bear">'+fm(min)+'</div></div>'+
      '<div class="cot-stat"><div class="cot-stat-label">Datapunkter</div><div class="cot-stat-val">'+data.length+'</div></div>';

  } catch(e) {
    document.getElementById('cotModalStats').innerHTML = '<div style="color:var(--bear)">Ingen historikk tilgjengelig for dette markedet</div>';
    console.error(e);
  }
}
