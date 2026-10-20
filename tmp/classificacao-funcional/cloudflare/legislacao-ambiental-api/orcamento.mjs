// Um objeto global: limite diário atômico, compartilhado entre regiões.
// Guarda apenas data e contador. Não guarda IP, perguntas ou respostas.
export class ChatBudget {
  constructor(state) { this.storage = state.storage; }
  async fetch(request) {
    if(request.method!=='POST') return new Response(null,{status:405});
    const day=new Date().toISOString().slice(0,10);
    const allowed=await this.storage.transaction(async tx=> {
      const previous=await tx.get('usage');
      const count=previous?.day===day?previous.count:0;
      if(count>=80) return false;
      await tx.put('usage',{day,count:count+1});
      return true;
    });
    return new Response(null,{status:allowed?204:429});
  }
}
