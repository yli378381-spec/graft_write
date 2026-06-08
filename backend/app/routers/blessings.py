"""Built-in blessing templates (祝福语模板).

The free tier ships a curated, hand-written template library that the mascot
"阿喜" presents. Users pick one, fill in a name and copy it manually. (AI
generation is reserved for the paid tiers.)
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from app import schemas

router = APIRouter(prefix="/api/blessings", tags=["blessings"])

# scene: thanks_wedding / thanks_moments / birthday / festival / return_gift
TEMPLATES: list[schemas.BlessingTemplate] = [
    schemas.BlessingTemplate(
        id="tw_elder",
        scene="thanks_wedding",
        relation="elder",
        title="婚礼答谢·长辈",
        content="尊敬的{name}，感谢您在我们大喜之日拨冗光临、厚礼相赠。您的祝福我们铭记于心，愿您福寿安康、阖家欢乐。晚辈敬上。",
    ),
    schemas.BlessingTemplate(
        id="tw_friend",
        scene="thanks_wedding",
        relation="friend",
        title="婚礼答谢·好友",
        content="亲爱的{name}，谢谢你来见证我们最幸福的一天！你的到来和心意让这场婚礼更圆满，愿我们的友谊像今天一样，长长久久。",
    ),
    schemas.BlessingTemplate(
        id="tw_colleague",
        scene="thanks_wedding",
        relation="colleague",
        title="婚礼答谢·同事",
        content="{name}，感谢你在百忙之中送上祝福与贺礼，能与你共事是我的幸运。愿你工作顺心、生活美满，常联系！",
    ),
    schemas.BlessingTemplate(
        id="tm_all",
        scene="thanks_moments",
        relation="all",
        title="朋友圈集体答谢",
        content="婚礼圆满礼成🌹 感谢每一位远道而来的亲友，谢谢你们的祝福与陪伴。未能一一当面致谢，在此一并道一声：谢谢你们，我们会幸福的！",
    ),
    schemas.BlessingTemplate(
        id="tm_group",
        scene="thanks_moments",
        relation="all",
        title="亲友群答谢",
        content="各位亲爱的家人朋友，我们的婚礼已圆满结束，感谢大家的到场与厚爱❤️ 你们的祝福是我们最珍贵的新婚礼物，愿好运也常伴你们左右！",
    ),
    schemas.BlessingTemplate(
        id="bd_elder",
        scene="birthday",
        relation="elder",
        title="生日祝福·长辈",
        content="{name}，祝您生日快乐！愿岁月温柔以待，身体健康、笑口常开，福气满满每一天。",
    ),
    schemas.BlessingTemplate(
        id="bd_friend",
        scene="birthday",
        relation="friend",
        title="生日祝福·好友",
        content="{name}，生日快乐🎂 愿你想要的都拥有，得不到的都释怀，新的一岁继续闪闪发光！",
    ),
    schemas.BlessingTemplate(
        id="fs_spring",
        scene="festival",
        relation="all",
        title="春节祝福·通用",
        content="{name}，新春快乐！愿新的一年顺顺利利、财源广进，全家平安喜乐，好事连连。",
    ),
    schemas.BlessingTemplate(
        id="fs_midautumn",
        scene="festival",
        relation="all",
        title="中秋祝福·通用",
        content="{name}，中秋快乐🌕 月圆人圆事事圆，愿你和家人团团圆圆、幸福美满。",
    ),
    schemas.BlessingTemplate(
        id="rg_all",
        scene="return_gift",
        relation="all",
        title="回礼答谢·通用",
        content="{name}，上次的喜事多亏有你捧场，这次小小心意还请笑纳😊 愿我们常来常往，情谊长存。",
    ),
]


@router.get("", response_model=list[schemas.BlessingTemplate])
def list_templates(
    scene: str | None = Query(default=None),
    relation: str | None = Query(default=None),
):
    rows = TEMPLATES
    if scene:
        rows = [t for t in rows if t.scene == scene]
    if relation:
        rows = [t for t in rows if t.relation in (relation, "all")]
    return rows


@router.get("/render", response_model=schemas.OkOut)
def render_template(id: str, name: str = Query(default="")):
    """Fill the {name} placeholder so the user can copy the final text."""
    tpl = next((t for t in TEMPLATES if t.id == id), None)
    if not tpl:
        return schemas.OkOut(ok=False, message="模板不存在")
    text = tpl.content.replace("{name}", name or "")
    return schemas.OkOut(ok=True, message=text)
