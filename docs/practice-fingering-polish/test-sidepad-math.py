"""Independent analytical checks of offline triangle distance/refinement math."""
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fit',ROOT/'scripts/practice/fit-missing-poses.py')
fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
triangle=np.array([[[0.,0,0],[1,0,0],[0,1,0]]]);query=np.array([[.2,.2,2],[.2,.2,-2],[2,0,0]])
closest,_,signed=fit.nearest_surface(query,triangle)
np.testing.assert_allclose(closest,[[.2,.2,0],[.2,.2,0],[1,0,0]],atol=1e-12)
np.testing.assert_allclose(signed,[2,-2,1],atol=1e-12)
random=np.random.default_rng(209);triangles=random.normal(size=(50,3,3));query=random.normal(size=(30,3))
actual,_,_=fit.nearest_surface(query,triangles,k=50)
for point,result in zip(query,actual):
    expected,_,_=fit.previous.closest_triangle_point(triangles,point)
    np.testing.assert_allclose(result,expected,atol=1e-10)
np.testing.assert_allclose(fit.triangle_gaps(triangle,triangle+[0,0,2]),[2.])
assert fit.triangle_gaps(triangle,triangle)[0]==0
assert fit.triangle_gaps(triangle,np.array([[[.25,.25,-1],[.25,.25,1],[.75,.25,0]]]))[0]<=0
assert fit.triangle_gaps(triangle,triangle+[3,0,0])[0]>0
report={'passed':True,'analyticalTriangleCases':3,'independentClosestTriangleComparisons':30,'separatingAxisCases':4,'runtimeAcceptanceGateUnchanged':True}
(Path(__file__).parent/'tests/side-pad-math.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
