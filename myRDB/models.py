import datetime
import json

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Date publisched')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Orga(models.Model):
    team = models.CharField(max_length=100)
    theme_owner = models.CharField(max_length=100)


class Department(models.Model):
    department_name = models.CharField(max_length=8)


class Group(models.Model):
    group_name = models.CharField(max_length=11)


class ZI_Organisation(models.Model):
    zi_organisation_name = models.CharField(max_length=5)


class TF_Application(models.Model):
    application_name = models.CharField(max_length=100)


CHOICES = [(1, ' '), (2, 'K'), (3, 'U')]


class TF(models.Model):
    tf_name = models.CharField(max_length=100)
    tf_description = models.CharField(max_length=300)
    tf_owner_orga = models.ForeignKey(Orga, on_delete=models.CASCADE)
    tf_application = models.ForeignKey(TF_Application, on_delete=models.CASCADE)
    criticality = models.CharField(choices=CHOICES, max_length=1)
    highest_criticality_in_AF = models.CharField(choices=CHOICES, max_length=1)


class GF(models.Model):
    gf_name = models.CharField(max_length=150)
    gf_description = models.CharField(max_length=250)
    tfs = models.ManyToManyField(TF, 'owningGF')


class AF(models.Model):
    af_name = models.CharField(max_length=150)
    af_description = models.CharField(max_length=250)
    af_applied = models.DateTimeField()
    af_valid_from = models.DateTimeField()
    af_valid_till = models.DateTimeField()
    gfs = models.ManyToManyField(GF, 'owningAF')


class Role(models.Model):
    role_name = models.CharField(max_length=150)
    role_description = models.CharField(max_length=250)
    afs = models.ManyToManyField(AF, 'owningRole')


class CustomAccountManager(BaseUserManager):
    def create_user(self, identity, password):
        user = self.model(identity=identity, password=password)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self.db)
        return user

    def create_superuser(self, identity, password):
        user = self.create_user(identity=identity, password=password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

    def get_by_natural_key(self, identity_):
        case_insensitive_identitiy_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        print(identity_)
        return self.get(**{case_insensitive_identitiy_field: identity_})


class User(AbstractUser):
    identity = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)
    orga_id = models.ForeignKey(Orga, on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    zi_organisation_id = models.ForeignKey(ZI_Organisation, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    direct_connect_afs = models.ManyToManyField(AF, 'afOwningUser')
    direct_connect_gfs = models.ManyToManyField(GF, 'gfOwningUser')
    direct_connect_tfs = models.ManyToManyField(TF, 'tfOwningUser')
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=32)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'identity'

    objects = CustomAccountManager()

    def natural_key(self):
        return self.identity

    def get_short_name(self):
        return self.identity

    def __str__(self):
        return self.identity

    def retrieve_related_rights(self, user, roles, afs, compareUser):
        tfList = []
        gfList = []
        afList = []
        gf_count = 0
        for af in afs:
            gfs = GF.objects.filter(owningAF__id=af.id)
            gf_count += gfs.count()
            for gf in gfs:
                tfs = TF.objects.filter(owningGF__id=gf.id)
                for tf in tfs:
                    # print(tf.tf_name)
                    tfList.append(tf)
                    gfList.append(gf)
                    afList.append(af)

        data = zip(tfList, gfList, afList)
        tf_count = len(tfList)
        try:
            self.prepareJSONdata(self, user.identity, tfList, gfList, afList, compareUser)
        except(IOError):
            print("error while prparing json for graph")

        return data, gf_count, tf_count

    def prepareJSONdata(self, identity, tfList, gfList, afList, compareUser):
        scatterData = []
        scatterIndex = 0

        zippedData = zip(afList, gfList, tfList)
        jsonDict = {}
        jsonDict["name"] = identity
        jsonDict["children"] = []

        for line in zippedData:
            scatterIndex += 1
            if line[0].af_applied != None:
                af_applied = line[0].af_applied.isoformat();
            else:
                af_applied = ""
            scatterData.append({"name": line[2].tf_name, "index": scatterIndex, "af_applied": af_applied})
            inGF = False
            inAF = False
            # print(line)
            for afDict in jsonDict["children"]:
                if line[0].af_name in afDict.values():
                    inAF = True
                    for gfDict in afDict["children"]:
                        if line[1].gf_name in gfDict.values():
                            inGF = True
                            break
                        else:
                            inGF = False
                    break
                else:
                    inAF = False

            if inAF:
                if inGF:
                    # print("af und gf existieren")
                    gfDict["children"].append({"name": line[2].tf_name, "size": 3000})
                else:
                    # print("gf existiert nicht")
                    afDict["children"].append(
                        {"name": line[1].gf_name, "children": [{"name": line[2].tf_name, "size": 3000}]})
            else:
                # print("af existiert nicht")
                jsonDict["children"].append(
                    {"name": line[0].af_name,
                     "children": [{"name": line[1].gf_name, "children": [{"name": line[2].tf_name, "size": 3000}]}]})

        if compareUser:
            path = 'myRDB/static/myRDB/data/compareGraphData.json'
        else:
            path = 'myRDB/static/myRDB/data/graphData.json'
        with open(path, 'w') as outfile:
            json.dump(jsonDict, outfile, indent=2)

        scatterData.sort(key=lambda r: r["af_applied"])
        with open('myRDB/static/myRDB/data/scatterGraphData.json', 'w') as outfile:
            json.dump(scatterData, outfile, indent=2)
