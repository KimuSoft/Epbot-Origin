# 디스코드 메세지 인텐트로 인한 검열 기능 사용 제한.
# From cogs/admin.py
'''
class DBManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 욕설추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설추가 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["yok"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 욕설 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 욕설삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")
        newwork = " ".join(args)
        badwords["yok"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 욕설 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 야한말추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")
        newwork = " ".join(args)
        badwords["emr"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 야한말 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 야한말삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 야한말삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["emr"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 야한말 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 정치언급추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 정치언급추가 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["jci"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 정치언급 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 정치언급삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 정치언급삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["jci"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 정치언급 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 목록(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 목록 <야한말/정치언급/욕설/변태/나쁜말/관리자>`")
            return None

        badwords = sj.get_json("bad_words.json")
        args = " ".join(args)
        embed = discord.Embed(title="목록", colour=0x4BC59F)
        if (
            args == "야한말"
            or args == "정치언급"
            or args == "욕설"
            or args == "변태"
            or args == "나쁜말"
        ):
            if args == "야한말":
                ya = "emr"
            elif args == "정치언급":
                ya = "jci"
            elif args == "욕설":
                ya = "yok"
            elif args == "변태":
                ya = "bta"
            elif args == "나쁜말":
                ya = "gcm"
            else:
                ya = "err"
            words = badwords[ya]
            num = 0
            while len(words) > 20:
                if len(words) > 20:
                    num = num + 1
                    li = ""
                    for i in words[:20]:
                        li += i + "\n"
                    embed.add_field(
                        name="{arg} {num}번 목록".format(arg=args, num=num),
                        value=li,
                        inline=True,
                    )
                    del words[:20]
                else:
                    break
            li = ""
            for i in words[:20]:
                li += i + "\n"
            embed.add_field(
                name="{arg} {num}번 목록".format(arg=args, num=num + 1),
                value=li,
                inline=True,
            )
            await ctx.send(embed=embed)
        elif args == "관리자":
            embed.add_field(
                name="{arg} 목록".format(arg=args),
                value=sj.get_json("permission.json")["user"],
                inline=True,
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("`이프야 목록 <야한말/정치언급/욕설/변태/나쁜말/관리자>`")
            return None
'''