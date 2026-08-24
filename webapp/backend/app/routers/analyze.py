from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.schemas import OptimizeRequest
from app.dependencies import verify_api_key, get_components, get_cache_key, llm_cache, CACHE_TTL
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/api/analyze")
async def analyze_syllabus(syllabus_data: Dict[str, Any], comps=Depends(get_components)):
    """Analyze syllabus for gaps and issues"""
    if not comps.gap_analyzer:
        raise HTTPException(status_code=503, detail="Gap Analyzer service unavailable")
        
    try:
        course_title = syllabus_data.get('course_title', 'Unknown')
        cache_hit = False
        
        if llm_cache is not None:
            key = get_cache_key("analyze", syllabus_data)
            cached = llm_cache.get(key)
            if cached is not None:
                logger.info(f"Cache HIT for analysis of '{course_title}'")
                cache_hit = True
                analysis = cached
        
        if not cache_hit:
            logger.info(f"Analyzing syllabus for course: {course_title}")
            analysis = comps.gap_analyzer.analyze(syllabus_data)
            
            if llm_cache is not None:
                llm_cache.set(key, analysis, expire=CACHE_TTL)
        
        return {
            "success": True,
            "analysis": analysis,
            "cached": cache_hit
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/optimize")
async def optimize_syllabus(request: OptimizeRequest, comps=Depends(get_components)):
    """Perform a complete optimization of the syllabus"""
    try:
        original_syllabus = request.syllabus_data
        course_title = original_syllabus.get('course_title', 'Unknown')
        
        # Check cache
        if llm_cache is not None:
            opt_key = get_cache_key("optimize", original_syllabus)
            cached_result = llm_cache.get(opt_key)
            if cached_result is not None:
                logger.info(f"Cache HIT for optimization of '{course_title}'")
                cached_result['cached'] = True
                return cached_result

        if not comps.content_optimizer:
            raise HTTPException(status_code=503, detail="Content Optimizer service unavailable")
            
        logger.info(f"Calling LLM for optimization of '{course_title}'...")
        optimization_result = comps.content_optimizer.optimize_full_syllabus(original_syllabus)
        
        optimized_syllabus = optimization_result.get('optimized_syllabus', original_syllabus)
        
        # Post-processing checks
        nep_2020_compliance = None
        try:
            from src.validation.nep_2020_validator import NEP2020Validator
            nep_validator = NEP2020Validator()
            nep_2020_compliance = nep_validator.validate(optimized_syllabus)
        except Exception as e:
            logger.error(f"NEP validation fail (recoverable): {e}")
            
        accreditation_compliance = None
        try:
            from src.validation.accreditation_checker import AccreditationChecker
            accred_checker = AccreditationChecker()
            accreditation_compliance = {
                'nba': accred_checker.check_nba_compliance(optimized_syllabus),
                'naac': accred_checker.check_naac_compliance(optimized_syllabus)
            }
        except Exception as e:
            logger.error(f"Accreditation validation fail (recoverable): {e}")

        # CO-PO Map
        co_po_mapping = None
        if comps.co_po_mapper:
            try:
                co_po_mapping = comps.co_po_mapper.map_co_to_po(
                    course_outcomes=optimized_syllabus.get('learning_outcomes', []),
                    program_outcomes=original_syllabus.get('program_outcomes', [f'PO{i+1}' for i in range(12)]),
                    domain=optimized_syllabus.get('domain', 'engineering')
                )
            except Exception as e:
                logger.error(f"CO-PO mapping on optimized syllabus failed: {e}")

        result = {
            'success': True,
            'original_syllabus': original_syllabus,
            'optimized_syllabus': optimized_syllabus,
            'optimization': {
                'changes_summary': optimization_result.get('changes_summary', []),
                'bloom_distribution': optimization_result.get('bloom_distribution', {}),
                'rationale': optimization_result.get('rationale', ''),
                'industry_relevance_score': optimization_result.get('industry_relevance_score', 0),
                'prerequisite_rationale': optimization_result.get('prerequisite_rationale', ''),
                'nep_2020_compliance': nep_2020_compliance,
                'accreditation_compliance': accreditation_compliance,
                'co_po_mapping': co_po_mapping
            },
            'cached': False
        }
        
        if llm_cache is not None:
            llm_cache.set(opt_key, result, expire=CACHE_TTL)
        
        return result
        
    except Exception as e:
        logger.error(f"Optimization pipeline failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
