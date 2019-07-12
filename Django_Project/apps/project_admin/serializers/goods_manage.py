from rest_framework import serializers

from goods.models import SKUSpecification, SKU, GoodsCategory,\
    SPU, SpecificationOption, SPUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU规格序列化器"""

    # 模型类默认自动构建关联表id字段，但序列化时不会自动映射此字段
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUSpecification  # 外键关联SKU表
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    """SKU表信息的序列化器"""

    # SKU模型类默认自动构建关联表id字段，但序列化时不会自动映射此字段
    category_id = serializers.IntegerField()
    spu_id = serializers.IntegerField()

    # 指定所属分类信息 关联嵌套返回
    category = serializers.StringRelatedField(read_only=True)
    # 指定所属spu表信息 关联嵌套返回
    spu = serializers.StringRelatedField(read_only=True)
    # 指定所SKU关联的所有选项信息 关联嵌套返回
    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSimpleSerializer(serializers.ModelSerializer):
    """商品SPU表序列化器"""

    class Meta:
        model = SPU
        fields = ['id', 'name']


class SPUOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化器"""

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""

    # SPUSpecification中的外键spu关联了SPU商品表
    spu_id = serializers.IntegerField(read_only=True)
    spu = serializers.StringRelatedField(read_only=True)

    # 使用规格选项序列化器进行关联序列化
    options = SPUOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'spu_id', 'spu', 'options']
