"""
Star Ratings Agent - StateGraph with Conditional Routing

Based on PA project's StateGraph pattern with added conditional routing for 3 pipelines.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from databricks.sdk import WorkspaceClient
from databricks import sql
from databricks.sdk.core import Config
from databricks.vector_search.client import VectorSearchClient
import json


class StarRatingState(TypedDict):
    """State for star ratings workflow"""
    messages: list[dict]
    query_type: Literal["measure_analysis", "improvement", "qa"] | None
    measure_data: str | None
    classification: dict | None
    gap_analysis: dict | None
    recommendations: dict | None
    knowledge: list | None
    final_answer: str | None


class StarRatingsAgent:
    """
    StateGraph agent for star ratings analysis.
    
    Workflow:
    1. Classify intent (which pipeline?)
    2. Route to appropriate specialist pipeline
    3. Execute pipeline steps (UC functions + vector search)
    4. Synthesize final response
    """
    
    def __init__(self, catalog: str, schema: str, warehouse_id: str, vector_endpoint: str):
        self.catalog = catalog
        self.schema = schema
        self.warehouse_id = warehouse_id
        self.vector_endpoint = vector_endpoint
        self.w = WorkspaceClient()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _get_sql_connection(self):
        """Get Databricks SQL connection (from PA project pattern)"""
        cfg = Config()
        return sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{self.warehouse_id}",
            credentials_provider=lambda: cfg.authenticate
        )
    
    def _call_uc_function(self, function_name: str, *args):
        """Call Unity Catalog AI function (from PA project pattern)"""
        conn = self._get_sql_connection()
        cursor = conn.cursor()
        
        args_str = ", ".join([f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in args])
        sql_query = f"SELECT {self.catalog}.{self.schema}.{function_name}({args_str}) AS result"
        
        try:
            cursor.execute(sql_query)
            result = cursor.fetchone()[0]
            return result
        finally:
            cursor.close()
            conn.close()
    
    def _vector_search(self, query: str, num_results: int = 3) -> list:
        """Vector search for HEDIS guidelines using SQL (works with service principal auth)"""
        index_name = f"{self.catalog}.{self.schema}.hedis_guidelines_index"
        print(f"📚 Vector Search (SQL): Querying index '{index_name}'")
        print(f"   Query: {query}")
        
        try:
            # Use SQL VECTOR_SEARCH function instead of SDK (auth works via SQL connection)
            conn = self._get_sql_connection()
            cursor = conn.cursor()
            
            # VECTOR_SEARCH SQL function
            sql_query = f"""
                SELECT doc_id, title, content
                FROM VECTOR_SEARCH(
                    index => '{index_name}',
                    query => '{query.replace("'", "''")}',
                    num_results => {num_results}
                )
            """
            
            print(f"   Executing SQL vector search...")
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            # Convert SQL results to expected format: [[doc_id, title, content], ...]
            data_array = [[row[0], row[1], row[2]] for row in results]
            
            print(f"   ✅ Found {len(data_array)} results via SQL")
            cursor.close()
            conn.close()
            return data_array
            
        except Exception as e:
            print(f"   ❌ Vector search error: {e}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return []
    
    # === INTENT CLASSIFICATION (Simple, Deterministic) ===
    
    def _classify_intent_node(self, state: StarRatingState) -> StarRatingState:
        """Classify user intent using keywords (NOT LLM - fast and deterministic)"""
        query = state["messages"][-1]["content"].lower()
        
        # Rule-based classification
        if any(kw in query for kw in ["gap", "analyze", "performance", "why", "problem", "low", "issue"]):
            state["query_type"] = "measure_analysis"
        elif any(kw in query for kw in ["improve", "recommend", "action", "increase", "fix", "intervention", "strategy"]):
            state["query_type"] = "improvement"
        else:
            state["query_type"] = "qa"
        
        print(f"🎯 Intent classified as: {state['query_type']}")
        return state
    
    def _route_to_pipeline(self, state: StarRatingState) -> str:
        """Router for conditional edges"""
        return state["query_type"]
    
    # === MEASURE ANALYSIS PIPELINE ===
    
    def _measure_classify_node(self, state: StarRatingState) -> StarRatingState:
        """Classify measure performance"""
        print("📊 Classifying measure performance...")
        result = self._call_uc_function("star_measure_classify", state["measure_data"])
        state["classification"] = result
        return state
    
    def _measure_analyze_node(self, state: StarRatingState) -> StarRatingState:
        """Analyze performance gaps"""
        print("🔍 Analyzing performance gaps...")
        result = self._call_uc_function("star_gap_analyze", state["measure_data"])
        state["gap_analysis"] = result
        return state
    
    def _measure_search_node(self, state: StarRatingState) -> StarRatingState:
        """Search HEDIS guidelines"""
        print("📚 Searching HEDIS guidelines...")
        results = self._vector_search("HEDIS guidelines for measure improvement")
        state["knowledge"] = results
        return state
    
    # === IMPROVEMENT PIPELINE ===
    
    def _improve_recommend_node(self, state: StarRatingState) -> StarRatingState:
        """Generate recommendations"""
        print("💡 Generating improvement recommendations...")
        gap_data = json.dumps(state.get("gap_analysis", {})) if state.get("gap_analysis") else "{}"
        result = self._call_uc_function("star_improvement_recommend", state["measure_data"], gap_data)
        state["recommendations"] = result
        return state
    
    def _improve_search_node(self, state: StarRatingState) -> StarRatingState:
        """Search best practices"""
        print("📚 Searching quality improvement best practices...")
        results = self._vector_search("quality improvement interventions and best practices")
        state["knowledge"] = results
        return state
    
    # === Q&A PIPELINE ===
    
    def _qa_search_node(self, state: StarRatingState) -> StarRatingState:
        """Search knowledge base"""
        print("📚 Searching knowledge base...")
        query = state["messages"][-1]["content"]
        results = self._vector_search(query)
        state["knowledge"] = results
        return state
    
    def _qa_explain_node(self, state: StarRatingState) -> StarRatingState:
        """Generate explanation"""
        print("💬 Generating explanation...")
        context = json.dumps(state.get("knowledge", [])) if state.get("knowledge") else "{}"
        result = self._call_uc_function("star_explain", state.get("measure_data", ""), context)
        state["final_answer"] = result
        return state
    
    # === SYNTHESIS ===
    
    def _synthesize_node(self, state: StarRatingState) -> StarRatingState:
        """Synthesize final response"""
        print("🎨 Synthesizing final response...")
        parts = []
        
        if state.get("classification"):
            parts.append(f"**Classification**: {state['classification']}")
        if state.get("gap_analysis"):
            parts.append(f"**Gap Analysis**: {state['gap_analysis']}")
        if state.get("recommendations"):
            parts.append(f"**Recommendations**: {state['recommendations']}")
        if state.get("knowledge"):
            parts.append(f"**References**: Found {len(state['knowledge'])} relevant guidelines")
        
        state["final_answer"] = "\n\n".join(parts)
        return state
    
    # === BUILD GRAPH ===
    
    def _build_graph(self) -> StateGraph:
        """Build the StateGraph workflow"""
        workflow = StateGraph(StarRatingState)
        
        # Add all nodes
        workflow.add_node("classify_intent", self._classify_intent_node)
        
        # Measure analysis pipeline
        workflow.add_node("measure_classify", self._measure_classify_node)
        workflow.add_node("measure_analyze", self._measure_analyze_node)
        workflow.add_node("measure_search", self._measure_search_node)
        
        # Improvement pipeline
        workflow.add_node("improve_recommend", self._improve_recommend_node)
        workflow.add_node("improve_search", self._improve_search_node)
        
        # Q&A pipeline
        workflow.add_node("qa_search", self._qa_search_node)
        workflow.add_node("qa_explain", self._qa_explain_node)
        
        # Synthesis
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Entry point
        workflow.set_entry_point("classify_intent")
        
        # Conditional routing (NEW - key differentiator)
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_to_pipeline,
            {
                "measure_analysis": "measure_classify",
                "improvement": "improve_recommend",
                "qa": "qa_search"
            }
        )
        
        # Measure analysis pipeline edges
        workflow.add_edge("measure_classify", "measure_analyze")
        workflow.add_edge("measure_analyze", "measure_search")
        workflow.add_edge("measure_search", "synthesize")
        
        # Improvement pipeline edges
        workflow.add_edge("improve_recommend", "improve_search")
        workflow.add_edge("improve_search", "synthesize")
        
        # Q&A pipeline edges
        workflow.add_edge("qa_search", "qa_explain")
        workflow.add_edge("qa_explain", "synthesize")
        
        # End
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    def analyze_measure(self, measure_name: str, measure_data: str, user_query: str) -> dict:
        """Process a star ratings query"""
        print(f"\n{'='*60}")
        print(f"Processing Star Ratings Query")
        print(f"{'='*60}")
        print(f"Measure: {measure_name}")
        print(f"Query: {user_query}")
        print(f"{'='*60}\n")
        
        initial_state = {
            "messages": [{"role": "user", "content": user_query}],
            "query_type": None,
            "measure_data": measure_data,
            "classification": None,
            "gap_analysis": None,
            "recommendations": None,
            "knowledge": None,
            "final_answer": None
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "query_type": final_state["query_type"],
            "answer": final_state["final_answer"],
            "classification": final_state.get("classification"),
            "gaps": final_state.get("gap_analysis"),
            "recommendations": final_state.get("recommendations"),
            "knowledge": final_state.get("knowledge")  # Add vector search results
        }
