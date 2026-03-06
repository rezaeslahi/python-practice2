from typing import Sequence,Set,List
from dataclasses import dataclass
from enum import Enum


@dataclass
class QueryEvalCase():
    query_id:str
    retrieved_ids: Sequence[str]
    relevant_ids:Set[str]

class EvalMethod(str,Enum):
    percision = "percision"
    recall = "recall"
    mrr = "mrr"

cases = [
    QueryEvalCase(
        query_id="q1",
        retrieved_ids=["d1", "d2", "d3", "d4", "d5"],
        relevant_ids={"d3", "d10"},
    ),
    QueryEvalCase(
        query_id="q2",
        retrieved_ids=["d2", "d2", "d8"],  # duplicate
        relevant_ids={"d2"},
    ),
    QueryEvalCase(
        query_id="q3",
        retrieved_ids=[],
        relevant_ids={"d1"},
    ),
    QueryEvalCase(
        query_id="q4",
        retrieved_ids=["d9", "d10"],
        relevant_ids=set(),  # no ground truth
    ),
]

def evaluate_dateset(queries:List[QueryEvalCase],k:int)->dict[str,float]:
    dic = {}
    
    is_valid = validate(queries,k)
    if not is_valid:
        raise ValueError("Invalid inputs")

    perc = evaluate_at_k(queries,k,EvalMethod.percision)
    recall = evaluate_at_k(queries,k,EvalMethod.recall)
    mrr = evaluate_at_k(queries,k,EvalMethod.mrr)

    dic["precision_at_k"] = perc
    dic["recall_at_k"] = recall
    dic["mrr_at_k"] = mrr
    return dic

def validate(queries:List[QueryEvalCase],k:int)->bool:
    is_valid = True
    if k<=0:
        is_valid = False            
    return is_valid

def evaluate_at_k(queries:List[QueryEvalCase],k:int,method:EvalMethod)->float:
    score = 0
    count = len(queries)
    for i in range(count):
        eval = 0
        if method == EvalMethod.percision:
            eval = precision_at_k_for_one_query(queries[i],k)
        elif method == EvalMethod.recall:
            eval = recall_at_k_for_one_query(queries[i],k)
        elif method == EvalMethod.mrr:
            eval = mrr_at_k_for_one_query(queries[i],k)
            pass
        score += eval
    score /= count
    return score

def recall_at_k_for_one_query(query:QueryEvalCase,k:int)->float:
    """
    it checks if there is at least one relevant id in retrived ids
    """
    k_eff = min(k,len(query.retrieved_ids))
    if k_eff == 0:
        return 0
    retrived_ids_eff = set(query.retrieved_ids[0:k_eff])
    count = len(query.relevant_ids&retrived_ids_eff)
    return count/max(1,len(query.relevant_ids))
    
    


def precision_at_k_for_one_query(query:QueryEvalCase,k:int)->float:
    """
    How much of retrieved ids are actually relevant
    """
    k_eff = min(k,len(query.retrieved_ids))
    if k_eff == 0:
        return 0
    retrived_ids_eff = set(query.retrieved_ids[0:k_eff])    
    count = len(query.relevant_ids&retrived_ids_eff)
    return count/k_eff

def mrr_at_k_for_one_query(query:QueryEvalCase,k:int)->float:
    """
    How early the first relevant item is appread in the retrival
    """
    k_eff = min(k,len(query.retrieved_ids))
    if k_eff == 0:
        return 0   
    retrived_ids_eff = query.retrieved_ids[0:k_eff]
    # removing dupicates
    retrived_ids_eff = list(dict.fromkeys(retrived_ids_eff))
    for i,ret_id in enumerate(retrived_ids_eff,start=1):
        if ret_id in query.relevant_ids:
            return 1 / i
    return 0


if __name__ == "__main__":
    k= 3
    dic = evaluate_dateset(cases,k)
    print(dic)